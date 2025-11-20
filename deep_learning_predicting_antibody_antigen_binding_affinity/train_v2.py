"""
Train a new model.
"""
from __future__ import annotations

import time
from sklearn.model_selection import KFold, StratifiedKFold

import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from torch.autograd import Variable
from torch.utils.data import IterableDataset, dataloader
from multiprocessing.reduction import ForkingPickler
from sklearn.metrics import average_precision_score as average_precision
from tqdm import tqdm
from typing import Callable, NamedTuple, Optional
from collections import OrderedDict
import json
import sys
import os
import numpy as np
import argparse
import pandas as pd
import torch.optim as optim
from torch.optim import Optimizer
from src.models.mvsf import ModelAffinity
from src.utils import *
from multiprocessing.reduction import ForkingPickler
from torch.optim.lr_scheduler import LambdaLR, ReduceLROnPlateau
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from torch.cuda.amp import GradScaler, autocast
# from torcheval.metrics.functional import r2_score
from sklearn.metrics import r2_score
from scipy.stats import pearsonr 

default_collate_func = dataloader.default_collate

def default_collate_override(batch):
    dataloader._use_shared_memory = False
    return default_collate_func(batch)
setattr(dataloader, 'default_collate', default_collate_override)
for t in torch._storage_classes:
    if sys.version_info[0] == 2:
        if t in ForkingPickler.dispatch:
            del ForkingPickler.dispatch[t]
    else:
        if t in ForkingPickler._extra_reducers:
            del ForkingPickler._extra_reducers[t]

class TrainArguments(NamedTuple):
    cmd: str
    device: int
    train: str
    test: str
    no_augment: bool
    augment_weight: float
    weight_module1: float
    weight_module2: float
    num_epochs: int
    batch_size: int
    weight_decay: float
    lr: float
    kfolds: int
    outfile: Optional[str]
    save_prefix: Optional[str]
    checkpoint: Optional[str]
    seed: Optional[int]
    func: Callable[[TrainArguments], None]

def add_args(parser):
    data_grp = parser.add_argument_group("Data")
    contact_grp = parser.add_argument_group("Contact Module")
    train_grp = parser.add_argument_group("Training")
    misc_grp = parser.add_argument_group("Output and Device")

    # Data
    data_grp.add_argument("--train", default="datasets/pairs_sabdab.csv", help="list of training pairs")
    data_grp.add_argument("--test", default="datasets/pairs_benchmark.csv", help="list of validation/testing pairs")
    data_grp.add_argument("--seq-path", default="datasets/seq_natural.fasta")
    data_grp.add_argument("--feature-path", default="datasets/seq_natural_embedding.csv")
    data_grp.add_argument("--no-augment", default=True, help="data is automatically augmented by adding (B A) for all pairs (A B). Set this flag to not augment data",)
    data_grp.add_argument("--augment-weight", type=float, default=0.5, help="weight of augment data",)

    # Model
    contact_grp.add_argument("--weight-module1", type=float, default=1, help="weight of module1",)
    contact_grp.add_argument("--weight-module2", type=float, default=1, help="weight of module1",)

    # Training
    train_grp.add_argument("--num-epochs", type=int, default=30, help="number of epochs",)
    train_grp.add_argument("--batch-size", type=int, default=16, help="minibatch size (default: 16)",)
    train_grp.add_argument("--weight-decay", type=float, default=0.00001, help="L2 regularization /0.0001",)  # 正则化项的设置
    train_grp.add_argument("--lr", type=float, default=0.00001, help="learning rate",)
    train_grp.add_argument("--kfolds", type=int, default=10)
    train_grp.add_argument("--cross-validate", default=True, help="cross validate",)

    # Output and Device
    misc_grp.add_argument("-o", "--outfile", help="output file path (default: stdout)")
    misc_grp.add_argument("--save-prefix", help="path prefix for saving models")
    misc_grp.add_argument("-d", "--device", type=int, required=True, help="compute device to use")
    misc_grp.add_argument("--checkpoint", help="checkpoint model to start training from")
    misc_grp.add_argument("--seed", help="Set random seed", type=int)
    return parser

def predict_affinity(model, Lchain, Hchain, antigen, embedding_tensor, aaindex_feature, use_cuda):
    b = len(Hchain)
    lchain_embeddings = []
    hchain_embeddings = []
    ag_embeddings = []

    lchain_aaindex = []
    hchain_aaindex = []
    ag_aaindex = []

    for i in range(b):
        lchain_embedding = embedding_tensor[Lchain[i]]
        hchain_embedding = embedding_tensor[Hchain[i]]
        ag_embedding = embedding_tensor[antigen[i]]

        lchain_aaindex.append(aaindex_feature[Lchain[i]])
        hchain_aaindex.append(aaindex_feature[Hchain[i]])
        ag_aaindex.append(aaindex_feature[antigen[i]])

        lchain_embeddings.append(lchain_embedding)
        hchain_embeddings.append(hchain_embedding)
        ag_embeddings.append(ag_embedding)

    if use_cuda:
        lchain_embeddings = torch.stack(lchain_embeddings, 0).cuda()
        hchain_embeddings = torch.stack(hchain_embeddings, 0).cuda()
        ag_embeddings = torch.stack(ag_embeddings, 0).cuda()

        lchain_aaindex = torch.stack(lchain_aaindex, 0).cuda()
        hchain_aaindex = torch.stack(hchain_aaindex, 0).cuda()
        ag_aaindex = torch.stack(ag_aaindex, 0).cuda()



    ph = model.predict(lchain_aaindex, hchain_aaindex, ag_aaindex, lchain_embeddings, hchain_embeddings, ag_embeddings)
    return ph

def model_eval(
    model,
    test_iterator,
    embedding_tensors,
    aaindex_feature,
    write,
    weight1,
    weight2,
    use_cuda,
    delta_g_mean,   
    delta_g_std    
):
    model.eval()

    p_hat_list = []
    true_y_list = []

    with torch.no_grad():
        for lchain, hchain, antigen, y in test_iterator:
            ph = predict_affinity(
                model, lchain, hchain, antigen, embedding_tensors, aaindex_feature, use_cuda
            )
            p_hat_list.append(ph.reshape(-1).cpu())  
            true_y_list.append(y.reshape(-1).cpu())  

    y_norm = torch.cat(true_y_list, 0).float()      
    yhat_norm = torch.cat(p_hat_list, 0).float()    

    # loss in normalized space
    # criterion = nn.MSELoss()
    criterion = nn.SmoothL1Loss(beta=0.5)
    loss = criterion(yhat_norm, y_norm)             

    # ---------- invert BOTH to original ΔG units (NEW) ----------
    y_orig = y_norm * delta_g_std + delta_g_mean       
    yhat_orig = yhat_norm * delta_g_std + delta_g_mean 

    mse = torch.mean((yhat_orig - y_orig) ** 2).item()    
    rmse = mse ** 0.5                                     
    mae = torch.mean(torch.abs(yhat_orig - y_orig)).item()

    y_np = y_orig.numpy()
    yhat_np = yhat_orig.numpy()

    if np.isclose(y_np.var(), 0.0):                       
        r_2 = 0.0
    else:
        r_2 = float(r2_score(y_np, yhat_np))              

    if y_np.std() > 0 and yhat_np.std() > 0:              
        p = float(pearsonr(y_np, yhat_np)[0])             
    else:
        p = 0.0                                           

    return float(loss.item()), rmse, mae, r_2, p          


def train_model(args, output):
    batch_size = args.batch_size
    use_cuda = (args.device > -1) and torch.cuda.is_available()

    train_fi = args.train
    train_df = pd.read_csv(train_fi)
    test_fi = args.test
    test_df = pd.read_csv(test_fi)

    lr = args.lr            # suggested: 3e-4 [IMPROVED: choose in CLI]
    num_epochs = args.num_epochs  # suggested: 50
    digits = int(np.floor(np.log10(num_epochs))) + 1
    save_prefix = args.save_prefix
    weight1 = args.weight_module1  # 1.5 [IMPROVED: in CLI]
    weight2 = args.weight_module2  # 1.0

    # ---------- TARGET NORMALIZATION STATS (z-score) ----------
    delta_g_mean = float(train_df["delta_g"].mean())
    delta_g_std  = float(train_df["delta_g"].std())

    log(f"delta_g mean (train) = {delta_g_mean}", file=output)
    log(f"delta_g std  (train) = {delta_g_std}",  file=output)
    output.flush()

    # still OK to save min/max for record, but we don't use them any more
    global_min_val = float(train_df["delta_g"].min())
    global_max_val = float(train_df["delta_g"].max())

    log(f"Global delta_g MIN = {global_min_val}", file=output)
    log(f"Global delta_g MAX = {global_max_val}", file=output)
    output.flush()

    with open("train_deltaG_minmax.json", "w") as f:
        json.dump(
            {"min_val": global_min_val, "max_val": global_max_val},
            f,
            indent=4
        )

    if args.cross_validate:
        k_folds = args.kfolds
        kfold = KFold(n_splits=k_folds, shuffle=True, random_state=42)

        global_best_rmse = float("inf")
        global_best_r2 = -float("inf")
        global_best_fold = None
        global_best_epoch = None
        global_best_model_path = None

        all_folds_metrics = []

        os.makedirs('checkpoints', exist_ok=True)

        # [IMPROVED] early stopping patience (can also be an arg)
        early_stop_patience = 10    # epochs without improvement per fold [IMPROVED]

        for fold, (train_ids, test_ids) in enumerate(kfold.split(train_df)):
            print(f'******************************** FOLD {fold} ******************************')
            log(f'******************************** FOLD {fold} ******************************', file=output)

            train_df_fold = train_df.iloc[train_ids].reset_index(drop=True)
            test_df_fold = train_df.iloc[test_ids].reset_index(drop=True)

            train_df_fold.columns = ["light", "heavy", "antigen", "delta_g"]
            test_df_fold.columns = ["light", "heavy", "antigen", "delta_g"]

            train_l_fold = train_df_fold["light"]
            train_h_fold = train_df_fold["heavy"]
            train_ag_fold = train_df_fold["antigen"]
            train_delta_g = train_df_fold["delta_g"].values.astype("float32")

            test_l_fold = test_df_fold["light"]
            test_h_fold = test_df_fold["heavy"]
            test_ag_fold = test_df_fold["antigen"]
            test_delta_g = test_df_fold["delta_g"].values.astype("float32")

            # ---------- z-score normalization (NO sign flip) ----------
            train_y_fold = (train_delta_g - delta_g_mean) / delta_g_std
            test_y_fold  = (test_delta_g  - delta_g_mean) / delta_g_std

            train_y_fold = torch.from_numpy(train_y_fold).float()
            test_y_fold  = torch.from_numpy(test_y_fold).float()

            train_dataset_fold = PairedDataset(train_l_fold, train_h_fold, train_ag_fold, train_y_fold)
            train_iterator_fold = torch.utils.data.DataLoader(
                train_dataset_fold,
                batch_size=batch_size,
                collate_fn=collate_paired_sequences,
                shuffle=True,
                pin_memory=False,
                drop_last=False,
            )
            log(f"Loaded {len(train_l_fold)} training pairs", file=output)
            output.flush()

            test_dataset_fold = PairedDataset(test_l_fold, test_h_fold, test_ag_fold, test_y_fold)
            test_iterator_fold = torch.utils.data.DataLoader(
                test_dataset_fold,
                batch_size=batch_size,
                collate_fn=collate_paired_sequences,
                shuffle=False,
                pin_memory=False,
                drop_last=False,
            )

            all_proteins = (set(train_l_fold)
                            .union(train_h_fold)
                            .union(train_ag_fold)
                            .union(test_l_fold)
                            .union(test_h_fold)
                            .union(test_ag_fold))
            fastaPath = args.seq_path
            embeddingPath = args.feature_path
            embeddings = embed_dict(fastaPath, embeddingPath)
            log("Embedded successfully...", file=output)
            aaindex_feature = seq_aaindex_dict(all_proteins, fastaPath)

            model = ModelAffinity(batch_size, use_cuda)
            model.use_cuda = use_cuda
            if use_cuda:
                model.cuda()

            params = [p for p in model.parameters() if p.requires_grad]

            # base_optimizer = optim.SGD
            base_optimizer = torch.optim.Adam   # you already changed this [OK]
            optimizer = SAM(params, base_optimizer, lr=lr, weight_decay=args.weight_decay)

            # scheduler driven by validation RMSE
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode='min', factor=0.5, patience=5
            )

            batch_report_fmt = ("[{}/{}] training {:.1%}: Loss={:.6}, MSE={:.6}, MAE={:.6}")
            epoch_report_fmt = (
                "-----------------------------------Finished Epoch {}/{}: Loss={:.6}, RMSE={:.6}, MAE={:.6}, r_2={:.6}, p={:.6}")

            N = len(train_iterator_fold) * batch_size
            fold_metrics = []

            # [IMPROVED] track best RMSE in this fold for early stopping
            best_rmse_fold = float("inf")          # [IMPROVED]
            epochs_no_improve = 0                  # [IMPROVED]

            for epoch in range(num_epochs):
                # [IMPROVED] let scheduler manage LR; remove manual /10
                print("lr:", optimizer.param_groups[0]['lr'])

                model.train()
                n = 0
                loss_accum = 0.0
                mse_accum = 0.0
                mae_accum = 0.0
                optimizer.zero_grad()

                criterion = nn.SmoothL1Loss(beta=0.5)  # [IMPROVED] define once per epoch

                for (lchain, hchain, antigen, y) in train_iterator_fold:
                    if use_cuda:
                        y = y.cuda()
                    y = y.float()

                    phat = predict_affinity(
                        model, lchain, hchain, antigen, embeddings, aaindex_feature, use_cuda=use_cuda
                    )
                    phat = phat.float().view(-1)

                    b = len(y)
                    loss = criterion(phat, y)

                    loss.backward()
                    # [IMPROVED] gradient clipping to stabilize training
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # [IMPROVED]

                    if use_cuda:
                        y_cpu = y.cpu()
                        phat_cpu = phat.cpu()
                    else:
                        y_cpu = y
                        phat_cpu = phat

                    with torch.no_grad():
                        mse = torch.mean((y_cpu - phat_cpu) ** 2).item()
                        mae = torch.mean(torch.abs(y_cpu - phat_cpu)).item()

                    n += b
                    delta = b * (loss.item() - loss_accum)
                    loss_accum += delta / n
                    delta = b * (mse - mse_accum)
                    mse_accum += delta / n
                    delta = b * (mae - mae_accum)
                    mae_accum += delta / n

                    report = (n - b) // 100 < n // 100

                    optimizer.step()
                    optimizer.zero_grad()

                    if report:
                        tokens = [epoch + 1, num_epochs, n / N, loss_accum, mse_accum, mae_accum]
                        log(batch_report_fmt.format(*tokens), file=output)
                        output.flush()

                # ---- validation ----
                write = (epoch + 1 == 30)
                inter_loss, inter_rmse, inter_mae, inter_r_2, inter_p = model_eval(
                    model,
                    test_iterator_fold,
                    embeddings,
                    aaindex_feature,
                    write,
                    weight1,
                    weight2,
                    use_cuda,
                    delta_g_mean,
                    delta_g_std
                )

                tokens = [epoch + 1, num_epochs, inter_loss, inter_rmse, inter_mae, inter_r_2, inter_p]

                fold_metrics.append({
                    "fold": fold,
                    "epoch": epoch + 1,
                    "inter_loss": float(inter_loss),
                    "inter_rmse": float(inter_rmse),
                    "inter_mae": float(inter_mae),
                    "inter_r_2": float(inter_r_2),
                    "inter_p": float(inter_p),
                    "lr": float(optimizer.param_groups[0]['lr']),
                })

                scheduler.step(inter_rmse)

                log(epoch_report_fmt.format(*tokens), file=output)
                output.flush()

                # [IMPROVED] early stopping check
                if inter_rmse < best_rmse_fold - 1e-3:      # small tolerance [IMPROVED]
                    best_rmse_fold = inter_rmse
                    epochs_no_improve = 0
                else:
                    epochs_no_improve += 1

                if epochs_no_improve >= early_stop_patience:  # [IMPROVED]
                    log(f"Early stopping on fold {fold} at epoch {epoch+1}", file=output)
                    break

                # checkpoint (optional to keep only best)
                ckpt_name = f"model_fold{fold}_epoch{epoch+1}.pt"
                ckpt_path = os.path.join('checkpoints', ckpt_name)
                torch.save({"model_state_dict": model.state_dict(),
                            "fold": fold,
                            "epoch": epoch + 1}, ckpt_path)

                output.flush()

            all_folds_metrics.extend(fold_metrics)

        if len(all_folds_metrics) > 0:
            df_all = pd.DataFrame(all_folds_metrics)
            df_all.to_csv("all_folds_metrics.csv", index=False)

    else:
        # ---------- unify with z-score normalization ----------
        train_df.columns = ["light", "heavy", "antigen", "delta_g"]
        test_df.columns = ["light", "heavy", "antigen", "delta_g"]

        train_l = train_df["light"]
        train_h = train_df["heavy"]
        train_ag = train_df["antigen"]
        train_delta_g = train_df["delta_g"].values.astype("float32")

        test_l = test_df["light"]
        test_h = test_df["heavy"]
        test_ag = test_df["antigen"]
        test_delta_g = test_df["delta_g"].values.astype("float32")

        # [IMPROVED] z-score using SAME delta_g_mean/std from above
        train_y = (train_delta_g - delta_g_mean) / delta_g_std   # [IMPROVED]
        test_y  = (test_delta_g  - delta_g_mean) / delta_g_std   # [IMPROVED]

        train_y = torch.from_numpy(train_y).float()              # [IMPROVED]
        test_y  = torch.from_numpy(test_y).float()               # [IMPROVED]

        train_dataset = PairedDataset(train_l, train_h, train_ag, train_y)
        train_iterator = torch.utils.data.DataLoader(
            train_dataset,
            batch_size=batch_size,
            collate_fn=collate_paired_sequences,
            shuffle=True,
            pin_memory=False,
            drop_last=False,
        )
        log(f"Loaded {len(train_l)} training pairs", file=output)
        output.flush()

        test_dataset = PairedDataset(test_l, test_h, test_ag, test_y)
        test_iterator = torch.utils.data.DataLoader(
            test_dataset,
            batch_size=batch_size,
            collate_fn=collate_paired_sequences,
            shuffle=False,
            pin_memory=False,
            drop_last=False,
        )

        log(f"Loaded {len(test_l)} test pairs", file=output)
        log("Loading embeddings...", file=output)
        output.flush()

        all_proteins = set(train_l).union(train_h).union(train_ag).union(test_l).union(test_h).union(test_ag)

        fastaPath = args.seq_path
        embeddingPath = args.feature_path
        embeddings = embed_dict(fastaPath, embeddingPath)
        log("Embedded successfully...", file=output)
        aaindex_feature = seq_aaindex_dict(all_proteins, fastaPath)

        model = ModelAffinity(batch_size, use_cuda)
        if use_cuda:
            model.cuda()

        params = [p for p in model.parameters() if p.requires_grad]
        # [IMPROVED] simple Adam (no SAM) is fine here for debugging
        optimizer = torch.optim.Adam(params, lr=lr, weight_decay=args.weight_decay)  # [IMPROVED]

        batch_report_fmt = ("[{}/{}] training {:.1%}: Loss={:.6}, MSE={:.6}, MAE={:.6}")
        epoch_report_fmt = (
            "-----------------------------------Finished Epoch {}/{}: Loss={:.6}, RMSE={:.6}, MAE={:.6}, r_2={:.6}, p={:.6}")

        N = len(train_iterator) * batch_size
        criterion = nn.SmoothL1Loss(beta=0.5)  # [IMPROVED]

        for epoch in range(num_epochs):
            model.train()
            n = 0
            loss_accum = 0.0
            mse_accum = 0.0
            mae_accum = 0.0
            optimizer.zero_grad()

            for (lchain, hchain, antigen, y) in train_iterator:
                if use_cuda:
                    y = y.cuda()
                y = y.float()

                phat = predict_affinity(
                    model, lchain, hchain, antigen, embeddings, aaindex_feature, use_cuda=use_cuda
                )
                phat = phat.float().view(-1)

                loss = criterion(phat, y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)  # [IMPROVED]
                optimizer.step()
                optimizer.zero_grad()

                # logging
                if use_cuda:
                    y_cpu = y.cpu()
                    phat_cpu = phat.cpu()
                else:
                    y_cpu = y
                    phat_cpu = phat

                with torch.no_grad():
                    mse = torch.mean((y_cpu - phat_cpu) ** 2).item()
                    mae = torch.mean(torch.abs(y_cpu - phat_cpu)).item()

                b = len(y_cpu)
                n += b
                delta = b * (loss.item() - loss_accum)
                loss_accum += delta / n
                delta = b * (mse - mse_accum)
                mse_accum += delta / n
                delta = b * (mae - mae_accum)
                mae_accum += delta / n

            # eval
            model.eval()
            with torch.no_grad():
                write = False
                inter_loss, inter_rmse, inter_mae, inter_r_2, inter_p = model_eval(
                    model,
                    test_iterator,
                    embeddings,
                    aaindex_feature,
                    write,
                    weight1,
                    weight2,
                    use_cuda,
                    delta_g_mean,
                    delta_g_std
                )

                tokens = [epoch + 1, num_epochs, inter_loss, inter_rmse, inter_mae, inter_r_2, inter_p]
                log(epoch_report_fmt.format(*tokens), file=output)
                output.flush()

                os.makedirs('checkpoints', exist_ok=True)
                ckpt_name = f"model_epoch{epoch+1}.pt"
                ckpt_path = os.path.join('checkpoints', ckpt_name)
                torch.save({
                    "model_state_dict": model.state_dict(),
                    "epoch": epoch + 1,
                    "args": vars(args) if hasattr(args, "__dict__") else {},
                }, ckpt_path)



def main(args):
    output = args.outfile
    if output is None:
        output = sys.stdout
    else:
        output = open(output, "w")

    log(f'Called as: {" ".join(sys.argv)}', file=output, print_also=True)

    # Set the device
    device = args.device
    use_cuda = (device > -1) and torch.cuda.is_available()
    if use_cuda:
        torch.cuda.set_device(device)
        log(
            f"Using CUDA device {device} - {torch.cuda.get_device_name(device)}",
            file=output,
            print_also=True,
        )
    else:
        log("Using CPU", file=output, print_also=True)
        device = "cpu"

    if args.seed is not None:
        np.random.seed(args.seed)
        torch.manual_seed(args.seed)
    train_model(args, output)

    output.close()




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser)
    main(parser.parse_args())


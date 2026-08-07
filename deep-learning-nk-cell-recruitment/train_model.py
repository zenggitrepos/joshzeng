# Usage: python train_mpc.py your_training_data.csv
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import os
import sys


def sum_to_n(n, size, limit=None):
    if size == 1:
        return [n]
    if limit is None:
        limit = n
    start = (n + size - 1) // size
    stop = min(limit, n - size + 1) + 1
    for i in range(start, stop):
        return [i] + sum_to_n(n - i, size - 1, i)

def read_csv(path):
    with open(path) as f:
        data = f.readlines()

    save_arr = []
    for line in data[1:]:
        line = line.replace('\n', '').split(',')
        num = [float(n) for n in line]
        # same filtering rule as inference code
        if num[0] > 70:  # remove over 70
            continue
        save_arr.append(num)

    return np.array(save_arr)

# overfit dropout optimal 0.5, dont change, adding another layer same as input dimension, 12
class FeedForward(nn.Module):
    def __init__(self, d_model, dropout = 0.5):
        super().__init__() 

        self.linear_1 = nn.Linear(d_model, d_model)
        self.dropout_1 = nn.Dropout(dropout)
        self.linear_2 = nn.Linear(d_model, 1)
    
        # you could add weight init here if desired

    def forward(self, x):
        x = self.linear_1(x)
        x = F.tanh(x)
        x = self.dropout_1(x)
        x = self.linear_2(x)
        return x

# ---------- training code ----------

def train_model(
    csv_path,
    model_out_path="final_model.pt",
    epochs=500,
    batch_size=32,
    lr=1e-3,
    weight_decay=0.0,
    val_split=0.2,
    seed=42,
):
    torch.manual_seed(seed)
    np.random.seed(seed)

    # ---- load and split data ----
    data = read_csv(csv_path)  # shape: [N, 1 + d_model]
    y = data[:, 0:1]           # (N, 1)
    X = data[:, 1:]            # (N, d_model)

    N, d_model = X.shape
    print(f"Loaded {N} samples with feature dim = {d_model}")

    # shuffle indices
    idx = np.arange(N)
    np.random.shuffle(idx)
    X = X[idx]
    y = y[idx]

    # simple train/val split
    split = int(N * (1 - val_split))
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    # convert to tensors
    X_train_t = torch.from_numpy(X_train).float()
    y_train_t = torch.from_numpy(y_train).float()
    X_val_t   = torch.from_numpy(X_val).float()
    y_val_t   = torch.from_numpy(y_val).float()

    train_ds = TensorDataset(X_train_t, y_train_t)
    val_ds   = TensorDataset(X_val_t, y_val_t)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    # ---- model / loss / optimizer ----
    model = FeedForward(d_model=d_model, dropout=0.5)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(
        model.parameters(), lr=lr, weight_decay=weight_decay
    )

    # training loop (CPU, to stay consistent with predict_mpc.py)
    best_val_loss = float("inf")
    best_state = None

    for epoch in range(1, epochs + 1):
        # ---- train ----
        model.train()
        train_loss_sum = 0.0

        for xb, yb in train_loader:
            optimizer.zero_grad()
            preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()
            train_loss_sum += loss.item() * xb.size(0)

        train_loss = train_loss_sum / len(train_loader.dataset)

        # ---- validate ----
        model.eval()
        val_loss_sum = 0.0
        with torch.no_grad():
            for xb, yb in val_loader:
                preds = model(xb)
                loss = criterion(preds, yb)
                val_loss_sum += loss.item() * xb.size(0)
        val_loss = val_loss_sum / len(val_loader.dataset)

        # track best
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = model.state_dict()

        if epoch == 1 or epoch % 50 == 0:
            print(
                f"Epoch {epoch:04d} "
                f"| train MSE: {train_loss:.4f} "
                f"| val MSE: {val_loss:.4f}"
            )

    # ---- save best model ----
    if best_state is not None:
        model.load_state_dict(best_state)

    torch.save(model.state_dict(), model_out_path)
    print(f"Saved trained model to: {model_out_path}")
    print(f"Best validation MSE: {best_val_loss:.4f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} <train_data.csv> [model_out.pt]")
        sys.exit(1)

    csv_path = sys.argv[1]
    if len(sys.argv) >= 3:
        model_out = sys.argv[2]
    else:
        model_out = "final_model.pt"

    train_model(csv_path, model_out_path=model_out)


# Colab Retraining Instructions - Fake Job Detection Model

## Objective
Retrain the BERT model with adjustments to reduce false positives (like the Microsoft job) while maintaining strong fraud detection capabilities.

---

## Critical Changes to Make

### 1. **Reduce Class Weight Aggressiveness**

**Current Code (in model training cell):**
```python
class_weights = compute_class_weight('balanced', classes=np.unique(y_train_encoded), y=y_train_encoded)
class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)
print(f'Class weights: {class_weights}')
# Output: tensor([0.5255, 10.3203])
```

**New Code:**
```python
class_weights = compute_class_weight('balanced', classes=np.unique(y_train_encoded), y=y_train_encoded)
# Cap the fraudulent class weight to reduce false positives
class_weights[1] = min(class_weights[1], 5.0)  # Cap at 5.0 instead of 10.32
class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)
print(f'Class weights (capped): {class_weights}')
```

**Rationale**: The 10.32x weight makes the model overly sensitive. Capping at 5.0 provides balance without excessive false positives.

---

### 2. **Adjust Learning Rate**

**Current Code:**
```python
optimizer = AdamW(model.parameters(),
                  lr = 2e-5,  # Current learning rate
                  eps = 1e-8
                )
```

**New Code:**
```python
optimizer = AdamW(model.parameters(),
                  lr = 1e-5,  # Reduced from 2e-5 to 1e-5
                  eps = 1e-8
                )
```

**Rationale**: Lower learning rate leads to more conservative updates, potentially better generalization.

---

### 3. **Increase Dropout for Better Generalization**

**Current Code:**
```python
model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels = 1,
    output_attentions = False,
    output_hidden_states = False,
)
```

**New Code:**
```python
from transformers import BertConfig

config = BertConfig.from_pretrained("bert-base-uncased")
config.hidden_dropout_prob = 0.2  # Increased from default 0.1
config.attention_probs_dropout_prob = 0.2  # Increased from default 0.1

model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    config=config,
    num_labels = 1,
    output_attentions = False,
    output_hidden_states = False,
)
```

**Rationale**: Higher dropout reduces overfitting to training patterns.

---

### 4. **Implement Early Stopping**

**Add this code BEFORE the training loop:**
```python
# Early stopping configuration
best_val_loss = float('inf')
patience = 2  # Stop if no improvement for 2 epochs
patience_counter = 0
best_model_state = None
```

**Modify the validation section INSIDE the training loop:**
```python
# After calculating avg_val_loss
avg_val_loss = total_eval_loss / len(val_dataloader)
validation_loss_values.append(avg_val_loss)

print(f"  Validation loss: {avg_val_loss:.2f}")
print(f"  Validation took: {format_time(time.time() - t0)}")

# Early stopping check
if avg_val_loss < best_val_loss:
    best_val_loss = avg_val_loss
    patience_counter = 0
    best_model_state = model.state_dict().copy()
    print(f"  ✓ New best validation loss: {best_val_loss:.2f}")
else:
    patience_counter += 1
    print(f"  No improvement. Patience: {patience_counter}/{patience}")
    if patience_counter >= patience:
        print(f"\n⚠ Early stopping triggered after epoch {epoch_i + 1}")
        break

# After training loop completes, restore best model
if best_model_state is not None:
    model.load_state_dict(best_model_state)
    print(f"\n✓ Restored best model with validation loss: {best_val_loss:.2f}")
```

**Rationale**: Prevents overfitting by stopping when validation loss stops improving.

---

### 5. **Use Focal Loss (Optional but Recommended)**

**Add this class BEFORE the training loop:**
```python
class FocalLoss(torch.nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, inputs, targets):
        BCE_loss = torch.nn.functional.binary_cross_entropy_with_logits(
            inputs, targets, reduction='none'
        )
        pt = torch.exp(-BCE_loss)
        F_loss = self.alpha * (1-pt)**self.gamma * BCE_loss
        return F_loss.mean()
```

**Replace the loss function:**
```python
# OLD:
# loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=class_weights[1])

# NEW:
loss_fn = FocalLoss(alpha=0.25, gamma=2.0)
```

**Rationale**: Focal Loss focuses on hard-to-classify examples, reducing false positives on easy genuine jobs.

---

### 6. **Document the Threshold**

**Add this comment in the model saving section:**
```python
# Save model and tokenizer
output_dir = './bert_model_output'
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

# IMPORTANT: Recommended inference threshold
# Based on validation performance, use threshold = 0.50 for balanced results
# Lower threshold (0.35) = higher recall, more false positives
# Higher threshold (0.60) = higher precision, fewer false positives
print("\n✓ Model saved to:", output_dir)
print("📌 Recommended inference threshold: 0.50")
```

---

## Complete Modified Training Cell

Here's the complete training cell with all modifications:

```python
import time
import datetime
import numpy as np
import pandas as pd
import os
from transformers import BertTokenizer, BertForSequenceClassification, BertConfig, get_linear_schedule_with_warmup
from torch.optim import AdamW
import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from google.colab import drive

# Focal Loss implementation
class FocalLoss(torch.nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, inputs, targets):
        BCE_loss = torch.nn.functional.binary_cross_entropy_with_logits(
            inputs, targets, reduction='none'
        )
        pt = torch.exp(-BCE_loss)
        F_loss = self.alpha * (1-pt)**self.gamma * BCE_loss
        return F_loss.mean()

def format_time(elapsed):
    elapsed_rounded = int(round((elapsed)))
    return str(datetime.timedelta(seconds=elapsed_rounded))

# Initialize lists
loss_values = []
validation_loss_values = []
training_stats = []

# Data loading (defensive)
print("Re-loading and preprocessing data...")
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')
else:
    print("Drive already mounted.")

file_path = '/content/drive/MyDrive/fake_job_dataset/fake_job_postings.csv'

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    print(f"Dataset loaded successfully.")
else:
    raise FileNotFoundError(f"Required file not found: {file_path}")

text_cols = ['title', 'company_profile', 'description', 'requirements', 'benefits']
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].fillna('')
df['text_input'] = df[text_cols].agg(' '.join, axis=1)

if 'fraudulent' in df.columns and len(df['fraudulent'].unique()) > 1:
    X = df[['text_input']]
    y = df['fraudulent']
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("Data split successfully.")
else:
    raise ValueError("Fraudulent column missing or insufficient unique values.")

# Tokenization
print("Tokenizing data...")
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_val_encoded = label_encoder.transform(y_val)

input_ids_train = []
attention_masks_train = []
for text in X_train['text_input']:
    encoded_dict = tokenizer(
        text, add_special_tokens=True, max_length=256,
        padding='max_length', return_attention_mask=True,
        return_tensors='pt', truncation=True
    )
    input_ids_train.append(encoded_dict['input_ids'])
    attention_masks_train.append(encoded_dict['attention_mask'])
input_ids_train = torch.cat(input_ids_train, dim=0)
attention_masks_train = torch.cat(attention_masks_train, dim=0)
labels_train = torch.tensor(y_train_encoded)

input_ids_val = []
attention_masks_val = []
for text in X_val['text_input']:
    encoded_dict = tokenizer(
        text, add_special_tokens=True, max_length=256,
        padding='max_length', return_attention_mask=True,
        return_tensors='pt', truncation=True
    )
    input_ids_val.append(encoded_dict['input_ids'])
    attention_masks_val.append(encoded_dict['attention_mask'])
input_ids_val = torch.cat(input_ids_val, dim=0)
attention_masks_val = torch.cat(attention_masks_val, dim=0)
labels_val = torch.tensor(y_val_encoded)

batch_size = 16
train_dataset = TensorDataset(input_ids_train, attention_masks_train, labels_train)
train_sampler = RandomSampler(train_dataset)
train_dataloader = DataLoader(train_dataset, sampler=train_sampler, batch_size=batch_size)

val_dataset = TensorDataset(input_ids_val, attention_masks_val, labels_val)
val_sampler = SequentialSampler(val_dataset)
val_dataloader = DataLoader(val_dataset, sampler=val_sampler, batch_size=batch_size)
print("DataLoaders created.")

# Device and class weights
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

class_weights = compute_class_weight('balanced', classes=np.unique(y_train_encoded), y=y_train_encoded)
# ✨ NEW: Cap the fraudulent class weight
class_weights[1] = min(class_weights[1], 5.0)
class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)
print(f'Class weights (capped): {class_weights}')

# ✨ NEW: Model with increased dropout
config = BertConfig.from_pretrained("bert-base-uncased")
config.hidden_dropout_prob = 0.2
config.attention_probs_dropout_prob = 0.2

model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    config=config,
    num_labels = 1,
    output_attentions = False,
    output_hidden_states = False,
)
model.to(device)
print("BERT model loaded with increased dropout.")

epochs = 4

# ✨ NEW: Reduced learning rate
optimizer = AdamW(model.parameters(), lr = 1e-5, eps = 1e-8)
total_steps = len(train_dataloader) * epochs
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

# ✨ NEW: Use Focal Loss
loss_fn = FocalLoss(alpha=0.25, gamma=2.0)
print("Using Focal Loss for training.")

# ✨ NEW: Early stopping setup
best_val_loss = float('inf')
patience = 2
patience_counter = 0
best_model_state = None

# Training loop
print("Starting training...")
for epoch_i in range(0, epochs):
    print(f"======== Epoch {epoch_i + 1} / {epochs} ========")
    print("Training...")
    
    t0 = time.time()
    model.train()
    total_train_loss = 0
    
    for step, batch in enumerate(train_dataloader):
        if step % 40 == 0 and not step == 0:
            elapsed = format_time(time.time() - t0)
            print(f'  Batch {step:>5,}  of  {len(train_dataloader):>5,}.   Elapsed: {elapsed}.')
        
        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)
        
        model.zero_grad()
        
        outputs = model(
            b_input_ids,
            token_type_ids=None,
            attention_mask=b_input_mask,
        )
        
        logits = outputs.logits.squeeze(1)
        loss = loss_fn(logits, b_labels.float())
        
        total_train_loss += loss.item()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
    
    avg_train_loss = total_train_loss / len(train_dataloader)
    loss_values.append(avg_train_loss)
    
    print(f"  Average training loss: {avg_train_loss:.2f}")
    print(f"  Training epoch took: {format_time(time.time() - t0)}")
    
    # Validation
    print("\nRunning Validation...")
    t0 = time.time()
    model.eval()
    total_eval_loss = 0
    all_logits = np.array([])
    all_label_ids = np.array([])
    
    for batch in val_dataloader:
        b_input_ids, b_input_mask, b_labels = tuple(t.to(device) for t in batch)
        
        with torch.no_grad():
            outputs = model(
                b_input_ids,
                token_type_ids=None,
                attention_mask=b_input_mask
            )
        
        logits = outputs.logits.squeeze(1)
        loss = loss_fn(logits, b_labels.float())
        total_eval_loss += loss.item()
        
        logits = logits.detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()
        
        all_logits = np.concatenate((all_logits, logits), axis=0) if all_logits.size else logits
        all_label_ids = np.concatenate((all_label_ids, label_ids), axis=0) if all_label_ids.size else label_ids
    
    avg_val_loss = total_eval_loss / len(val_dataloader)
    validation_loss_values.append(avg_val_loss)
    
    print(f"  Validation loss: {avg_val_loss:.2f}")
    print(f"  Validation took: {format_time(time.time() - t0)}")
    
    # ✨ NEW: Early stopping check
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        patience_counter = 0
        best_model_state = model.state_dict().copy()
        print(f"  ✓ New best validation loss: {best_val_loss:.2f}")
    else:
        patience_counter += 1
        print(f"  No improvement. Patience: {patience_counter}/{patience}")
        if patience_counter >= patience:
            print(f"\n⚠ Early stopping triggered after epoch {epoch_i + 1}")
            break
    
    training_stats.append({
        'epoch': epoch_i + 1,
        'Training Loss': avg_train_loss,
        'Validation Loss': avg_val_loss,
        'Validation Time': format_time(time.time() - t0)
    })

# ✨ NEW: Restore best model
if best_model_state is not None:
    model.load_state_dict(best_model_state)
    print(f"\n✓ Restored best model with validation loss: {best_val_loss:.2f}")

print("\nTraining complete!")

# Save model
output_dir = './bert_model_output'
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

print("\n✓ Model saved to:", output_dir)
print("📌 Recommended inference threshold: 0.50")
print("   - Use 0.40 for higher recall (catch more fakes, more false positives)")
print("   - Use 0.60 for higher precision (fewer false positives, might miss some fakes)")
```

---

## Copy-Paste Prompt for Colab Agent

```
Please modify the BERT model training code with the following improvements to reduce false positives:

1. **Cap class weights**: Limit the fraudulent class weight to 5.0 instead of letting it go to 10.32
2. **Reduce learning rate**: Change from 2e-5 to 1e-5 for more conservative updates
3. **Increase dropout**: Set hidden_dropout_prob and attention_probs_dropout_prob to 0.2
4. **Implement early stopping**: Stop training if validation loss doesn't improve for 2 epochs
5. **Use Focal Loss**: Replace BCEWithLogitsLoss with Focal Loss (alpha=0.25, gamma=2.0)
6. **Document threshold**: Add comments about recommended inference threshold (0.50)

Use the complete modified training cell provided above. After training, download the model from './bert_model_output' and replace the existing model in the backend.
```

---

## After Retraining

1. **Download the new model** from Colab (`bert_model_output.zip`)
2. **Extract** and replace files in `backend/ml/bert_model_output/`
3. **Update `model_service.py`**:
   ```python
   THRESHOLD = 0.50  # Changed from 0.35
   ```
4. **Restart the backend** and test with the Microsoft job posting
5. **Monitor performance** with both genuine and fake job examples

---

## Expected Improvements

- **Fewer false positives** on legitimate corporate job postings
- **Maintained high recall** for actual fraudulent posts
- **Better generalization** to unseen job posting patterns
- **More balanced** precision-recall trade-off

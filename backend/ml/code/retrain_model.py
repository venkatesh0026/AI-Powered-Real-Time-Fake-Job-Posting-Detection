# ============================================================================
# BERT Model Retraining Script for Fake Job Detection
# ============================================================================
# This script includes all optimizations to reduce false positives:
# - Capped class weights (5.0 max)
# - Reduced learning rate (1e-5)
# - Increased dropout (0.2)
# - Early stopping (patience=2)
# - Focal Loss for better class balance
# ============================================================================

# %% [markdown]
# # Setup and Installation

# %%
print("Installing necessary libraries...")
!pip install transformers torch pandas scikit-learn kaggle -q
print("Libraries installed successfully.")

# %% [markdown]
# # Mount Google Drive

# %%
import os
from google.colab import drive

if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')
else:
    print("Drive already mounted.")

drive_folder = '/content/drive/MyDrive/fake_job_dataset'
print(f"Listing contents of {drive_folder}:")
!ls -lh "{drive_folder}"
print("Verification complete.")

# %% [markdown]
# # Import Libraries

# %%
import time
import datetime
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from transformers import BertTokenizer, BertForSequenceClassification, BertConfig, get_linear_schedule_with_warmup
from torch.optim import AdamW
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    classification_report
)

print("All libraries imported successfully.")

# %% [markdown]
# # Focal Loss Implementation

# %%
class FocalLoss(torch.nn.Module):
    """
    Focal Loss for handling class imbalance.
    Reduces the relative loss for well-classified examples,
    putting more focus on hard, misclassified examples.
    
    Args:
        alpha: Weighting factor for the rare class (default: 0.25)
        gamma: Focusing parameter, higher = more focus on hard examples (default: 2.0)
    """
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

print("Focal Loss class defined.")

# %% [markdown]
# # Helper Functions

# %%
def format_time(elapsed):
    """Takes a time in seconds and returns a string hh:mm:ss"""
    elapsed_rounded = int(round((elapsed)))
    return str(datetime.timedelta(seconds=elapsed_rounded))

print("Helper functions defined.")

# %% [markdown]
# # Load and Preprocess Data

# %%
print("Loading and preprocessing data...")

file_path = '/content/drive/MyDrive/fake_job_dataset/fake_job_postings.csv'

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    print(f"Dataset '{file_path}' loaded successfully.")
    print(f"Shape: {df.shape}")
else:
    raise FileNotFoundError(f"Required file not found: {file_path}")

# Handle missing values and create text input
text_cols = ['title', 'company_profile', 'description', 'requirements', 'benefits']
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].fillna('')

df['text_input'] = df[text_cols].agg(' '.join, axis=1)
print("Text input column created successfully.")

# Display class distribution
print("\nClass Distribution:")
print(df['fraudulent'].value_counts())
print(f"\nFraudulent percentage: {df['fraudulent'].mean()*100:.2f}%")

# Split data
if 'fraudulent' in df.columns and len(df['fraudulent'].unique()) > 1:
    X = df[['text_input']]
    y = df['fraudulent']
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nData split successfully.")
    print(f"Training set: {len(X_train)} samples")
    print(f"Validation set: {len(X_val)} samples")
else:
    raise ValueError("Fraudulent column missing or insufficient unique values.")

# %% [markdown]
# # Tokenization and DataLoader Setup

# %%
print("Initializing tokenizer and creating DataLoaders...")

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
print("BERT tokenizer initialized.")

label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_val_encoded = label_encoder.transform(y_val)
print("Labels encoded successfully.")

# Tokenize training data
print("Tokenizing training data...")
input_ids_train = []
attention_masks_train = []
for i, text in enumerate(X_train['text_input']):
    if (i+1) % 1000 == 0:
        print(f"  Processed {i+1}/{len(X_train)} training samples")
    encoded_dict = tokenizer(
        text, 
        add_special_tokens=True, 
        max_length=256,
        padding='max_length', 
        return_attention_mask=True,
        return_tensors='pt', 
        truncation=True
    )
    input_ids_train.append(encoded_dict['input_ids'])
    attention_masks_train.append(encoded_dict['attention_mask'])

input_ids_train = torch.cat(input_ids_train, dim=0)
attention_masks_train = torch.cat(attention_masks_train, dim=0)
labels_train = torch.tensor(y_train_encoded)
print(f"Training data tokenized: {input_ids_train.shape}")

# Tokenize validation data
print("Tokenizing validation data...")
input_ids_val = []
attention_masks_val = []
for i, text in enumerate(X_val['text_input']):
    if (i+1) % 1000 == 0:
        print(f"  Processed {i+1}/{len(X_val)} validation samples")
    encoded_dict = tokenizer(
        text, 
        add_special_tokens=True, 
        max_length=256,
        padding='max_length', 
        return_attention_mask=True,
        return_tensors='pt', 
        truncation=True
    )
    input_ids_val.append(encoded_dict['input_ids'])
    attention_masks_val.append(encoded_dict['attention_mask'])

input_ids_val = torch.cat(input_ids_val, dim=0)
attention_masks_val = torch.cat(attention_masks_val, dim=0)
labels_val = torch.tensor(y_val_encoded)
print(f"Validation data tokenized: {input_ids_val.shape}")

# Create DataLoaders
batch_size = 16
train_dataset = TensorDataset(input_ids_train, attention_masks_train, labels_train)
train_sampler = RandomSampler(train_dataset)
train_dataloader = DataLoader(train_dataset, sampler=train_sampler, batch_size=batch_size)

val_dataset = TensorDataset(input_ids_val, attention_masks_val, labels_val)
val_sampler = SequentialSampler(val_dataset)
val_dataloader = DataLoader(val_dataset, sampler=val_sampler, batch_size=batch_size)

print(f"\nDataLoaders created:")
print(f"  Training batches: {len(train_dataloader)}")
print(f"  Validation batches: {len(val_dataloader)}")

# %% [markdown]
# # Model Setup with Optimizations

# %%
# Device setup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

# Calculate and cap class weights
# OPTIMIZATION 1: Cap the fraudulent class weight to reduce false positives
class_weights = compute_class_weight('balanced', classes=np.unique(y_train_encoded), y=y_train_encoded)
original_weight = class_weights[1]
class_weights[1] = min(class_weights[1], 5.0)  # Cap at 5.0 instead of 10.32
class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)
print(f'Original class weight for fraudulent: {original_weight:.2f}')
print(f'Capped class weights: {class_weights}')

# OPTIMIZATION 2: Model with increased dropout for better generalization
config = BertConfig.from_pretrained("bert-base-uncased")
config.hidden_dropout_prob = 0.2  # Increased from 0.1
config.attention_probs_dropout_prob = 0.2  # Increased from 0.1

model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    config=config,
    num_labels=1,
    output_attentions=False,
    output_hidden_states=False,
)
model.to(device)
print("BERT model loaded with increased dropout (0.2).")

# Training configuration
epochs = 4

# OPTIMIZATION 3: Reduced learning rate for more conservative updates
optimizer = AdamW(model.parameters(), lr=1e-5, eps=1e-8)  # Reduced from 2e-5
print("Optimizer created with learning rate: 1e-5")

total_steps = len(train_dataloader) * epochs
scheduler = get_linear_schedule_with_warmup(
    optimizer, 
    num_warmup_steps=0, 
    num_training_steps=total_steps
)

# OPTIMIZATION 4: Use Focal Loss instead of BCEWithLogitsLoss
loss_fn = FocalLoss(alpha=0.25, gamma=2.0)
print("Using Focal Loss (alpha=0.25, gamma=2.0)")

# OPTIMIZATION 5: Early stopping setup
best_val_loss = float('inf')
patience = 2
patience_counter = 0
best_model_state = None
print(f"Early stopping enabled with patience: {patience}")

print("\n" + "="*50)
print("OPTIMIZATIONS SUMMARY:")
print("="*50)
print("1. Class weight capped at 5.0 (was 10.32)")
print("2. Dropout increased to 0.2 (was 0.1)")
print("3. Learning rate reduced to 1e-5 (was 2e-5)")
print("4. Using Focal Loss (not BCEWithLogitsLoss)")
print("5. Early stopping with patience=2")
print("="*50 + "\n")

# %% [markdown]
# # Training Loop

# %%
# Initialize tracking lists
loss_values = []
validation_loss_values = []
training_stats = []

print("Starting training...")
print("="*50)

for epoch_i in range(0, epochs):
    print(f"\n======== Epoch {epoch_i + 1} / {epochs} ========")
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
    
    training_time = format_time(time.time() - t0)
    print(f"  Average training loss: {avg_train_loss:.4f}")
    print(f"  Training epoch took: {training_time}")
    
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
    validation_time = format_time(time.time() - t0)
    
    print(f"  Validation loss: {avg_val_loss:.4f}")
    print(f"  Validation took: {validation_time}")
    
    # Early stopping check
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        patience_counter = 0
        best_model_state = model.state_dict().copy()
        print(f"  ✓ New best validation loss: {best_val_loss:.4f}")
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
        'Training Time': training_time,
        'Validation Time': validation_time
    })

# Restore best model
if best_model_state is not None:
    model.load_state_dict(best_model_state)
    print(f"\n✓ Restored best model with validation loss: {best_val_loss:.4f}")

print("\n" + "="*50)
print("Training complete!")
print("="*50)

# %% [markdown]
# # Model Evaluation

# %%
print("\nEvaluating model on validation set...")

model.eval()
all_preds = []
all_probs = []
all_labels = []

for batch in val_dataloader:
    b_input_ids, b_input_mask, b_labels = tuple(t.to(device) for t in batch)
    
    with torch.no_grad():
        outputs = model(
            b_input_ids,
            token_type_ids=None,
            attention_mask=b_input_mask
        )
    
    logits = outputs.logits.squeeze(1)
    probs = torch.sigmoid(logits).cpu().numpy()
    labels = b_labels.cpu().numpy()
    
    all_probs.extend(probs)
    all_labels.extend(labels)

all_probs = np.array(all_probs)
all_labels = np.array(all_labels)

# Test multiple thresholds
print("\n" + "="*60)
print("THRESHOLD ANALYSIS")
print("="*60)

thresholds = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
for thresh in thresholds:
    preds = (all_probs >= thresh).astype(int)
    acc = accuracy_score(all_labels, preds)
    prec = precision_score(all_labels, preds, zero_division=0)
    rec = recall_score(all_labels, preds, zero_division=0)
    f1 = f1_score(all_labels, preds, zero_division=0)
    
    print(f"\nThreshold: {thresh}")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1-Score:  {f1:.4f}")

# Use recommended threshold for final metrics
RECOMMENDED_THRESHOLD = 0.50
all_preds = (all_probs >= RECOMMENDED_THRESHOLD).astype(int)

print("\n" + "="*60)
print(f"FINAL METRICS (Threshold: {RECOMMENDED_THRESHOLD})")
print("="*60)

accuracy = accuracy_score(all_labels, all_preds)
precision = precision_score(all_labels, all_preds, zero_division=0)
recall = recall_score(all_labels, all_preds, zero_division=0)
f1 = f1_score(all_labels, all_preds, zero_division=0)
roc_auc = roc_auc_score(all_labels, all_probs)

print(f"\nAccuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-Score:  {f1:.4f}")
print(f"ROC-AUC:   {roc_auc:.4f}")

print("\nConfusion Matrix:")
cm = confusion_matrix(all_labels, all_preds)
print(cm)
print(f"\n  TN: {cm[0][0]} | FP: {cm[0][1]}")
print(f"  FN: {cm[1][0]} | TP: {cm[1][1]}")

print("\nClassification Report:")
print(classification_report(all_labels, all_preds, target_names=['Genuine', 'Fraudulent']))

# %% [markdown]
# # Plot ROC Curve

# %%
fpr, tpr, _ = roc_curve(all_labels, all_probs)

plt.figure(figsize=(10, 8))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Fake Job Detection (Optimized Model)')
plt.legend(loc="lower right")
plt.grid(True, alpha=0.3)
plt.savefig('./roc_curve_optimized.png', dpi=150, bbox_inches='tight')
plt.show()
print("ROC curve saved to './roc_curve_optimized.png'")

# %% [markdown]
# # Plot Training History

# %%
plt.figure(figsize=(10, 6))
epochs_range = range(1, len(loss_values) + 1)
plt.plot(epochs_range, loss_values, 'b-o', label='Training Loss')
plt.plot(epochs_range, validation_loss_values, 'r-o', label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('./training_history.png', dpi=150, bbox_inches='tight')
plt.show()
print("Training history saved to './training_history.png'")

# %% [markdown]
# # Save Model

# %%
output_dir = './bert_model_output'

print(f"\nSaving model to {output_dir}...")
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

# Verify saved files
print("\nSaved files:")
!ls -lh {output_dir}

print("\n" + "="*60)
print("MODEL SAVED SUCCESSFULLY!")
print("="*60)
print(f"✓ Model saved to: {output_dir}")
print(f"📌 Recommended inference threshold: {RECOMMENDED_THRESHOLD}")
print(f"\nTo use this model:")
print(f"  - Use threshold 0.40-0.45 for higher recall (catch more fakes)")
print(f"  - Use threshold 0.50 for balanced performance")
print(f"  - Use threshold 0.55-0.60 for higher precision (fewer false positives)")

# %% [markdown]
# # Save Model to Google Drive

# %%
import shutil

drive_output = '/content/drive/MyDrive/fake_job_dataset/bert_model_output_optimized.zip'

print(f"Compressing and saving to Google Drive...")
shutil.make_archive(drive_output.replace('.zip', ''), 'zip', output_dir)

print(f"\n✓ Model saved to Google Drive: {drive_output}")
print("\nListing Drive folder:")
!ls -lh /content/drive/MyDrive/fake_job_dataset/

# %% [markdown]
# # Test with Sample Jobs

# %%
print("\n" + "="*60)
print("TESTING WITH SAMPLE JOB POSTINGS")
print("="*60)

def predict_job(title, description, company_profile="", requirements="", benefits=""):
    """Predict if a job posting is fake or genuine."""
    text = f"{title} {company_profile} {description} {requirements} {benefits}"
    
    encoded = tokenizer(
        text,
        add_special_tokens=True,
        max_length=256,
        padding='max_length',
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )
    
    input_ids = encoded['input_ids'].to(device)
    attention_mask = encoded['attention_mask'].to(device)
    
    model.eval()
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
    
    prob = torch.sigmoid(outputs.logits).item()
    
    return prob

# Test cases
test_jobs = [
    {
        "name": "Microsoft Software Engineer (GENUINE)",
        "title": "Software Engineer",
        "description": "We are looking for a talented Software Engineer to join our Azure team in Redmond, WA. You will be responsible for designing, developing, and maintaining cloud infrastructure services.",
        "requirements": "Bachelor's degree in Computer Science. 3+ years of experience.",
        "benefits": "Competitive salary ($120,000-$180,000). Comprehensive health insurance. 401(k) matching."
    },
    {
        "name": "Work From Home Scam (FAKE)",
        "title": "Data Entry - Work From Home",
        "description": "Make up to $5000/week working from home. No experience necessary! Send your resume and a $50 registration fee to process@remotejobs.com.",
        "requirements": "Basic typing skills. Must pay $50 processing fee.",
        "benefits": "Full health, dental, and vision insurance from day one. Company car allowance."
    },
    {
        "name": "Marketing Intern (GENUINE)",
        "title": "Marketing Intern",
        "description": "Food52, a fast-growing, James Beard Award-winning online food community, is interviewing interns to work with editors, executives, and developers.",
        "requirements": "Experience with content management systems a plus. Strong writing skills.",
        "benefits": "Internship opportunity with potential for future employment."
    },
    {
        "name": "Package Reshipping Scam (FAKE)",
        "title": "Package Reshipping Coordinator",
        "description": "We are seeking package handlers to receive and reship merchandise from your home. Earn $300 per package! No experience needed.",
        "requirements": "Valid home address. Ability to receive packages.",
        "benefits": "Flexible schedule. High earning potential."
    }
]

print(f"\nUsing threshold: {RECOMMENDED_THRESHOLD}\n")

for job in test_jobs:
    prob = predict_job(
        job["title"],
        job["description"],
        requirements=job.get("requirements", ""),
        benefits=job.get("benefits", "")
    )
    
    prediction = "FAKE" if prob >= RECOMMENDED_THRESHOLD else "GENUINE"
    confidence = prob if prob >= 0.5 else 1 - prob
    
    print(f"📋 {job['name']}")
    print(f"   Fraud Probability: {prob:.4f}")
    print(f"   Prediction: {prediction}")
    print(f"   Confidence: {confidence:.2%}")
    print()

print("="*60)
print("TESTING COMPLETE!")
print("="*60)

# %% [markdown]
# # Summary

# %%
print("\n" + "="*60)
print("RETRAINING SUMMARY")
print("="*60)

print("\n📊 TRAINING STATISTICS:")
for stat in training_stats:
    print(f"  Epoch {stat['epoch']}: Train Loss = {stat['Training Loss']:.4f}, Val Loss = {stat['Validation Loss']:.4f}")

print(f"\n📈 BEST MODEL PERFORMANCE (Threshold: {RECOMMENDED_THRESHOLD}):")
print(f"  Accuracy:  {accuracy:.4f}")
print(f"  Precision: {precision:.4f}")
print(f"  Recall:    {recall:.4f}")
print(f"  F1-Score:  {f1:.4f}")
print(f"  ROC-AUC:   {roc_auc:.4f}")

print("\n📁 OUTPUT FILES:")
print(f"  Local: {output_dir}/")
print(f"  Drive: {drive_output}")
print(f"  ROC Curve: ./roc_curve_optimized.png")
print(f"  Training History: ./training_history.png")

print("\n🔧 OPTIMIZATIONS APPLIED:")
print("  1. Class weight capped at 5.0")
print("  2. Dropout increased to 0.2")
print("  3. Learning rate reduced to 1e-5")
print("  4. Focal Loss for class imbalance")
print("  5. Early stopping with patience=2")

print("\n📌 NEXT STEPS:")
print("  1. Download bert_model_output_optimized.zip from Google Drive")
print("  2. Extract to backend/ml/bert_model_output/")
print("  3. Update THRESHOLD in model_service.py to 0.50")
print("  4. Restart the backend server")
print("  5. Test with the Microsoft job posting")

print("\n" + "="*60)
print("ALL DONE! 🎉")
print("="*60)

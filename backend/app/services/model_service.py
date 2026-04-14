
import os
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import torch.nn.functional as F

class ModelService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Threshold from notebook analysis (prioritizing recall)
        self.THRESHOLD = 0.35  
        
        # Lazy loading flag
        self._load_attempted = False

    def ensure_model_loaded(self):
        # Only skip if we already successfully loaded the model
        if self.model is not None:
            return
        
        print("Attempting to lazy load model...")
        self.load_model()

    def load_model(self):
        import sys
        import traceback
        print("=" * 50, file=sys.stderr)
        print("[MODEL SERVICE] load_model() called", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        try:
            from app.utils.config import Config
            model_path = Config.get_model_path()
            print(f"[MODEL SERVICE] MODEL_PATH: {model_path}", file=sys.stderr)
            print(f"[MODEL SERVICE] CWD: {os.getcwd()}", file=sys.stderr)
            print(f"[MODEL SERVICE] Path exists: {os.path.exists(model_path) if model_path else False}", file=sys.stderr)
            
            if not model_path or not os.path.exists(model_path):
                print(f"[MODEL SERVICE] WARNING: Path not found! Running MOCK mode.", file=sys.stderr)
                return

            print(f"[MODEL SERVICE] Loading model on {self.device}...", file=sys.stderr)
            
            # Load Tokenizer and Model
            self.tokenizer = BertTokenizer.from_pretrained(model_path)
            print(f"[MODEL SERVICE] Tokenizer loaded!", file=sys.stderr)
            
            self.model = BertForSequenceClassification.from_pretrained(model_path)
            print(f"[MODEL SERVICE] Model loaded!", file=sys.stderr)
            
            self.model.to(self.device)
            self.model.eval()
            
            print("[MODEL SERVICE] SUCCESS - Model ready for inference!", file=sys.stderr)
            
        except Exception as e:
            print(f"[MODEL SERVICE] ERROR: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            self.model = None

    def preprocess(self, data):
        """
        Concatenates text fields similar to training:
        title + company_profile + description + requirements + benefits
        """
        text_parts = [
            data.get('title', ''),
            data.get('company_profile', ''),
            data.get('description', ''),
            data.get('requirements', ''),
            data.get('benefits', '')
        ]
        # Join with space and clean up extra whitespace
        full_text = ' '.join([str(p).strip() for p in text_parts if p])
        return full_text

    def predict(self, data):
        # Ensure model is attempted to be loaded
        self.ensure_model_loaded()

        # If model is not loaded, return mock response
        if self.model is None or self.tokenizer is None:
            return {
                'label': 'Genuine',
                'confidence': 0.98,
                'details': 'Mock Result: Model not loaded. No suspicious indicators found.',
                'is_mock': True
            }

        try:
            text = self.preprocess(data)
            
            # Tokenize
            encoded_dict = self.tokenizer(
                text,
                add_special_tokens=True,
                max_length=256,
                padding='max_length',
                return_attention_mask=True,
                return_tensors='pt',
                truncation=True
            )
            
            input_ids = encoded_dict['input_ids'].to(self.device)
            attention_masks = encoded_dict['attention_mask'].to(self.device)
            
            # Inference
            with torch.no_grad():
                outputs = self.model(input_ids, token_type_ids=None, attention_mask=attention_masks)
            
            logits = outputs.logits
            probs = torch.sigmoid(logits).cpu().numpy()[0][0] # Get probability for class 1 (Fake)
            
            # Classification based on threshold
            is_fraud = probs >= self.THRESHOLD
            
            label = 'Fake' if is_fraud else 'Genuine'
            confidence = float(probs) if is_fraud else float(1 - probs)
            
            return {
                'label': label,
                'confidence': confidence, 
                'probability_fraud': float(probs),
                'details': f"Analysis based on ML model (Threshold: {self.THRESHOLD})."
            }

        except Exception as e:
            print(f"Inference Error: {e}")
            raise Exception(f"Inference failed: {str(e)}")

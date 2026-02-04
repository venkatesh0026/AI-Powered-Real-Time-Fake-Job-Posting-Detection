#!/usr/bin/env python
"""
Verification Script for Fake Job Posting Detection System
Checks if all components are properly set up
"""

import os
import sys
from pathlib import Path
import json

class ProjectVerifier:
    """Verifies project setup"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.results = {
            'structure': [],
            'backend': [],
            'frontend': [],
            'ml': [],
            'docs': []
        }
        self.all_pass = True
    
    def check(self, category, name, condition, details=""):
        """Check and record result"""
        status = "✓" if condition else "✗"
        self.results[category].append({
            'name': name,
            'status': status,
            'details': details
        })
        if not condition:
            self.all_pass = False
    
    def print_category(self, category, title):
        """Print category results"""
        print(f"\n{title}")
        print("-" * 60)
        for item in self.results[category]:
            print(f"  {item['status']} {item['name']}")
            if item['details']:
                print(f"    {item['details']}")
    
    def verify_structure(self):
        """Verify folder structure"""
        print("\n" + "="*60)
        print("VERIFICATION: Fake Job Posting Detection System")
        print("="*60)
        
        backend = self.project_dir / "backend"
        frontend = self.project_dir / "frontend"
        ml = backend / "ml"
        
        # Backend structure
        self.check('structure', 'Backend folder exists', backend.exists())
        self.check('structure', 'Frontend folder exists', frontend.exists())
        self.check('structure', 'ML folder exists', ml.exists())
        
        # Backend files
        self.check('backend', 'main.py exists', (backend / "app" / "main.py").exists())
        self.check('backend', 'database.py exists', (backend / "app" / "database.py").exists())
        self.check('backend', 'requirements.txt exists', (backend / "requirements.txt").exists())
        self.check('backend', '.env.example exists', (backend / ".env.example").exists())
        self.check('backend', '.env exists', (backend / ".env").exists(), 
                  "Create from .env.example if missing")
        
        # ML scripts
        scripts_dir = ml / "scripts"
        self.check('ml', 'Scripts folder exists', scripts_dir.exists())
        self.check('ml', 'Data loader script', (scripts_dir / "01_data_loader.py").exists())
        self.check('ml', 'Preprocessing script', (scripts_dir / "02_preprocessing.py").exists())
        self.check('ml', 'Model architecture', (scripts_dir / "03_model_architecture.py").exists())
        self.check('ml', 'Training script', (scripts_dir / "04_train_model.py").exists())
        self.check('ml', 'Evaluation script', (scripts_dir / "05_evaluate_model.py").exists())
        self.check('ml', 'Main pipeline', (scripts_dir / "main_pipeline.py").exists())
        
        # ML dataset
        dataset = ml / "dataset" / "fake_job_postings.csv"
        self.check('ml', 'Dataset file', dataset.exists(), 
                  "Required for model training")
        
        # Frontend files
        self.check('frontend', 'package.json exists', (frontend / "package.json").exists())
        self.check('frontend', 'App.js exists', (frontend / "src" / "App.js").exists())
        self.check('frontend', 'Login page', (frontend / "src" / "pages" / "Login.js").exists())
        self.check('frontend', 'Dashboard page', (frontend / "src" / "pages" / "Dashboard.js").exists())
        self.check('frontend', 'Metrics page', (frontend / "src" / "pages" / "Metrics.js").exists())
        self.check('frontend', 'API client', (frontend / "src" / "api" / "apiClient.js").exists())
        
        # Documentation
        self.check('docs', 'README.md exists', (self.project_dir / "README.md").exists())
        self.check('docs', 'API documentation', (self.project_dir / "API_DOCUMENTATION.md").exists())
        self.check('docs', 'Project summary', (self.project_dir / "PROJECT_SUMMARY.md").exists())
        self.check('docs', 'Quick start script', (self.project_dir / "quickstart.py").exists())
    
    def verify_requirements(self):
        """Verify requirements files"""
        requirements_path = self.project_dir / "backend" / "requirements.txt"
        if requirements_path.exists():
            with open(requirements_path) as f:
                content = f.read()
            
            required_packages = ['fastapi', 'torch', 'pandas', 'scikit-learn']
            for pkg in required_packages:
                self.check('backend', f'{pkg} in requirements', pkg.lower() in content.lower())
    
    def check_configuration(self):
        """Check configuration files"""
        env_path = self.project_dir / "backend" / ".env"
        
        if env_path.exists():
            with open(env_path) as f:
                env_content = f.read()
            
            required_vars = ['SECRET_KEY', 'DATABASE_URL', 'ALGORITHM']
            for var in required_vars:
                self.check('backend', f'{var} in .env', var in env_content)
    
    def verify(self):
        """Run all verifications"""
        self.verify_structure()
        self.verify_requirements()
        self.check_configuration()
        
        # Print results
        self.print_category('structure', "FOLDER STRUCTURE")
        self.print_category('backend', "BACKEND SETUP")
        self.print_category('ml', "ML PIPELINE")
        self.print_category('frontend', "FRONTEND SETUP")
        self.print_category('docs', "DOCUMENTATION")
        
        # Summary
        print("\n" + "="*60)
        if self.all_pass:
            print("✓ PROJECT VERIFICATION PASSED")
            print("\nNext steps:")
            print("  1. cd project/backend")
            print("  2. python -m venv venv")
            print("  3. activate venv")
            print("  4. pip install -r requirements.txt")
            print("  5. python ml/scripts/main_pipeline.py  (train model)")
            print("  6. python -m uvicorn app.main:app --reload")
            print("\nIn another terminal:")
            print("  1. cd project/frontend")
            print("  2. npm install")
            print("  3. npm start")
            print("\nAccess at: http://localhost:3000")
        else:
            print("✗ PROJECT VERIFICATION FAILED")
            print("\nPlease check the issues above and ensure:")
            print("  - All files are created")
            print("  - Dataset is in ml/dataset/")
            print("  - .env file is configured")
            print("\nOr run quickstart.py for automated setup")
        print("="*60 + "\n")
        
        return self.all_pass

if __name__ == "__main__":
    verifier = ProjectVerifier()
    success = verifier.verify()
    sys.exit(0 if success else 1)

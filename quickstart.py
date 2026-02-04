#!/usr/bin/env python
"""
Quick Start Script for Fake Job Posting Detection System
Helps users set up and run the entire system
"""

import os
import sys
import subprocess
from pathlib import Path

class QuickStartGuide:
    """Quick start guide for the application"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.backend_dir = self.project_dir / "backend"
        self.frontend_dir = self.project_dir / "frontend"
    
    def print_header(self, text):
        """Print section header"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70 + "\n")
    
    def print_step(self, step_num, text):
        """Print step"""
        print(f"[STEP {step_num}] {text}")
    
    def check_python(self):
        """Check Python version"""
        print("Checking Python installation...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} installed")
        return True
    
    def check_node(self):
        """Check Node.js installation"""
        print("Checking Node.js installation...")
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Node.js {result.stdout.strip()} installed")
                return True
        except:
            pass
        print("❌ Node.js not found (optional for backend-only setup)")
        return False
    
    def setup_backend_venv(self):
        """Create virtual environment"""
        self.print_step(1, "Creating Python virtual environment...")
        
        venv_path = self.backend_dir / "venv"
        if venv_path.exists():
            print(f"✓ Virtual environment already exists at {venv_path}")
            return True
        
        try:
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], 
                          check=True, capture_output=True)
            print(f"✓ Virtual environment created at {venv_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_backend_deps(self):
        """Install backend dependencies"""
        self.print_step(2, "Installing backend dependencies...")
        
        venv_python = self.backend_dir / "venv" / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        
        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            print(f"❌ requirements.txt not found")
            return False
        
        try:
            subprocess.run([str(venv_python), '-m', 'pip', 'install', '-r', str(requirements_file)],
                          check=True, capture_output=True, timeout=300)
            print("✓ Backend dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
        except subprocess.TimeoutExpired:
            print("⚠ Installation timed out. Try running manually: pip install -r requirements.txt")
            return True
    
    def setup_env_file(self):
        """Setup .env file"""
        self.print_step(3, "Setting up .env file...")
        
        env_file = self.backend_dir / ".env"
        env_example = self.backend_dir / ".env.example"
        
        if env_file.exists():
            print("✓ .env file already exists")
            return True
        
        if env_example.exists():
            with open(env_example) as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print(f"✓ .env file created from template")
            return True
        
        # Create default .env
        default_env = """SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./fake_jobs.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
        with open(env_file, 'w') as f:
            f.write(default_env)
        print("✓ Default .env file created")
        return True
    
    def check_dataset(self):
        """Check if dataset exists"""
        self.print_step(4, "Checking dataset...")
        
        dataset_path = self.backend_dir / "ml" / "dataset" / "fake_job_postings.csv"
        if dataset_path.exists():
            print(f"✓ Dataset found at {dataset_path}")
            return True
        
        print(f"❌ Dataset not found at {dataset_path}")
        print("   Please place fake_job_postings.csv in the dataset folder")
        return False
    
    def train_model(self):
        """Train the model"""
        self.print_step(5, "Training ML model...")
        
        print("Starting model training (this may take 5-10 minutes)...")
        
        venv_python = self.backend_dir / "venv" / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        
        try:
            os.chdir(self.backend_dir / "ml" / "scripts")
            subprocess.run([str(venv_python), 'main_pipeline.py'], check=True)
            print("✓ Model training completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Model training failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_backend(self):
        """Run backend server"""
        self.print_step(6, "Starting backend server...")
        
        print("\nStarting FastAPI server on http://localhost:8000")
        print("API documentation available at http://localhost:8000/docs")
        print("Press Ctrl+C to stop\n")
        
        venv_python = self.backend_dir / "venv" / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        
        try:
            subprocess.run([str(venv_python), '-m', 'uvicorn', 'app.main:app', 
                          '--reload', '--host', '0.0.0.0', '--port', '8000'],
                          cwd=str(self.backend_dir))
        except KeyboardInterrupt:
            print("\n✓ Backend server stopped")
    
    def run_frontend(self):
        """Run frontend server"""
        self.print_step(7, "Starting frontend server...")
        
        print("\nStarting React development server on http://localhost:3000")
        print("Press Ctrl+C to stop\n")
        
        try:
            subprocess.run(['npm', 'start'], cwd=str(self.frontend_dir))
        except KeyboardInterrupt:
            print("\n✓ Frontend server stopped")
        except FileNotFoundError:
            print("❌ npm not found. Please install Node.js")
    
    def run_full_setup(self):
        """Run complete setup"""
        self.print_header("FAKE JOB POSTING DETECTION SYSTEM - QUICK START")
        
        print("This script will:")
        print("  1. Check Python and Node.js installations")
        print("  2. Create virtual environment")
        print("  3. Install dependencies")
        print("  4. Setup configuration files")
        print("  5. Train ML model (if needed)")
        print("  6. Start backend and frontend servers")
        
        # Checks
        if not self.check_python():
            sys.exit(1)
        
        node_installed = self.check_node()
        
        # Backend setup
        print("\n" + "-"*70)
        print("BACKEND SETUP")
        print("-"*70 + "\n")
        
        if not self.setup_backend_venv():
            sys.exit(1)
        
        if not self.install_backend_deps():
            print("⚠ Skipping model training due to dependency issues")
        else:
            if not self.setup_env_file():
                print("⚠ Failed to setup .env")
            
            if self.check_dataset():
                train = input("\nTrain model now? (y/n): ").strip().lower()
                if train == 'y':
                    if not self.train_model():
                        print("⚠ Model training failed. Please run manually later")
        
        # Frontend setup
        if node_installed:
            print("\n" + "-"*70)
            print("FRONTEND SETUP")
            print("-"*70 + "\n")
            
            self.print_step(1, "Installing frontend dependencies...")
            try:
                subprocess.run(['npm', 'install'], cwd=str(self.frontend_dir), check=True)
                print("✓ Frontend dependencies installed")
            except:
                print("⚠ Failed to install frontend dependencies")
        
        # Start servers
        print("\n" + "-"*70)
        print("STARTING SERVERS")
        print("-"*70 + "\n")
        
        print("Choose which server to start:")
        print("  1. Backend only (FastAPI)")
        print("  2. Frontend only (React)")
        print("  3. Both (requires 2 terminals)")
        print("  4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            self.run_backend()
        elif choice == '2':
            if node_installed:
                self.run_frontend()
            else:
                print("❌ Node.js not installed")
        elif choice == '3':
            print("Starting both servers...\n")
            print("Backend will start in this terminal")
            print("Frontend will start in a new window")
            
            if sys.platform == "win32":
                import subprocess as sp
                sp.Popen(['start', 'cmd', '/k', f'cd {self.frontend_dir} && npm start'], 
                        shell=True)
            else:
                os.system(f'cd {self.frontend_dir} && npm start &')
            
            self.run_backend()
        
        self.print_header("Setup complete! Access the application at:")
        print("  Frontend: http://localhost:3000")
        print("  Backend: http://localhost:8000")
        print("  API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    guide = QuickStartGuide()
    guide.run_full_setup()

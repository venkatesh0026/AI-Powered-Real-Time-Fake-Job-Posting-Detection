import os

# Backend package root (backend/) - config.py is in backend/app/utils/
_BACKEND_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
# Default model path relative to backend root (backend/ml/bert_model_output)
_DEFAULT_MODEL_PATH = os.path.join(_BACKEND_ROOT, "ml", "bert_model_output")


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

    # Resolve model path so it works when running API from any cwd (e.g. API docs / uvicorn)
    @staticmethod
    def get_model_path():
        env_path = os.environ.get('MODEL_PATH')
        if env_path:
            path = os.path.abspath(env_path) if not os.path.isabs(env_path) else env_path
            # If env path doesn't exist (e.g. old fraud_model.pt), use default BERT dir
            if os.path.exists(path):
                return path

        # 1) Prefer path relative to this file (works for uvicorn, IDE, any cwd)
        if os.path.exists(_DEFAULT_MODEL_PATH):
            return _DEFAULT_MODEL_PATH

        # 2) Running from backend directory
        path_from_cwd = os.path.join(os.getcwd(), 'ml', 'bert_model_output')
        if os.path.exists(path_from_cwd):
            return path_from_cwd

        # 3) Running from project root
        path_from_root = os.path.join(os.getcwd(), 'backend', 'ml', 'bert_model_output')
        if os.path.exists(path_from_root):
            return path_from_root

        return _DEFAULT_MODEL_PATH

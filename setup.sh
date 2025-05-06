#!/bin/bash

# Add uv to PATH if not already there
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH
    if [[ "$SHELL" == *"zsh"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        source ~/.zshrc
    elif [[ "$SHELL" == *"bash"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        source ~/.bashrc
    fi
    
    echo "uv has been installed and added to your PATH"
    echo "Please restart your terminal or run: source ~/.${SHELL##*/}rc"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

# Install development dependencies
echo "Installing development dependencies..."
uv pip install -e ".[dev]"

# Install additional development tools
echo "Installing additional development tools..."
uv pip install ruff pytest-cov pre-commit

# Set up pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

echo "Setup complete! Virtual environment is activated."
echo "To activate the virtual environment in the future, run:"
echo "source .venv/bin/activate" 
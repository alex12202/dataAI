#!/bin/bash

# Ověření, že skript byl spuštěn pomocí `source`, ne samostatně
(return 0 2>/dev/null) || {
  echo "❌ Tento skript musíš spustit pomocí:"
  echo ""
  echo "   source $0"
  echo ""
  echo "💛 Jinak se virtuální prostředí a proměnné neaktivují správně!"
  exit 1
}

# Exit on error
set -e

echo "📦 Vytvářím virtuální prostředí..."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
echo "✅ Aktivováno: $(which python3)"

# Přidání Homebrew do PATH, pokud chybí
if [[ ":$PATH:" != *":/opt/homebrew/bin:"* ]]; then
  export PATH="/opt/homebrew/bin:$PATH"
fi

# Install brew (pokud není nainstalován)
if ! command -v brew &> /dev/null; then
  echo "👃 Instaluji Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  export PATH="/opt/homebrew/bin:$PATH"
fi

# Install unixODBC driver
echo "🔧 Instaluji unixODBC..."
brew install unixodbc

# Install pipx
if ! command -v pipx &> /dev/null; then
  echo "👃 Instaluji pipx..."
  brew install pipx
fi

export PATH="$HOME/.local/bin:$PATH"

# Install poetry
if ! command -v poetry &> /dev/null; then
  echo "👃 Instaluji Poetry přes pipx..."
  pipx install poetry
fi

# Install ODBC driver
echo "📥 Instaluji ODBC pro SQL Server..."
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew upgrade
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18

# Použij pip z virtuálního prostředí
python -m pip install --pre --no-binary :all: pyodbc

# Nastavení ODBCINI a ODBCSYSINI podle OS
if [[ "$(uname)" == "Darwin" ]]; then
  echo "🍏 Detekován macOS – používám odbc_mac.ini"
  export ODBCINI="$(pwd)/backend/connectors/odbc_mac.ini"
else
  echo "🐧 Detekován Linux – používám odbc.ini"
  export ODBCINI="$(pwd)/backend/connectors/odbc.ini"
fi

export ODBCSYSINI="$(pwd)/backend/connectors"

# Load environment proměnné
if [ -f ".env" ]; then
  echo "📄 Načítám .env soubor..."
  export $(grep -v '^#' .env | xargs)
fi

# Poetry install
echo "📦 Instalace závislostí přes Poetry..."
poetry install --no-root

# Workaround pro knihovny
export KMP_DUPLICATE_LIB_OK=TRUE

# 🔧 Vytvoření postactivate skriptu pro automatické exporty
POSTACTIVATE_PATH=".venv/bin/postactivate"
if [ ! -f "$POSTACTIVATE_PATH" ]; then
  echo "🔧 Vytvářím postactivate skript..."
  cat <<EOF > "$POSTACTIVATE_PATH"
# >>> Custom environment variables >>>
export ODBCINI="\$(pwd)/backend/connectors/odbc_mac.ini"
export ODBCSYSINI="\$(pwd)/backend/connectors"
export KMP_DUPLICATE_LIB_OK=TRUE

if [ -f "\$(pwd)/.env" ]; then
  export \$(grep -v '^#' "\$(pwd)/.env" | xargs)
fi
# <<< Custom environment variables <<<
EOF
  chmod +x "$POSTACTIVATE_PATH"
fi

# Patch .venv/bin/activate tak, aby vždy volal postactivate
ACTIVATE_PATH=".venv/bin/activate"
POSTACTIVATE_PATH=".venv/bin/postactivate"

# Vytvoř postactivate, pokud neexistuje
if [ ! -f "$POSTACTIVATE_PATH" ]; then
  echo "🔧 Vytvářím postactivate skript..."
  cat <<EOF > "$POSTACTIVATE_PATH"
# >>> Custom environment variables >>>
export ODBCINI="\$(pwd)/backend/connectors/odbc_mac.ini"
export ODBCSYSINI="\$(pwd)/backend/connectors"
export KMP_DUPLICATE_LIB_OK=TRUE

if [ -f "\$(pwd)/.env" ]; then
  export \$(grep -v '^#' "\$(pwd)/.env" | xargs)
fi
# <<< Custom environment variables <<<
EOF
  chmod +x "$POSTACTIVATE_PATH"
fi

# Přidej volání postactivate do activate skriptu (bez duplikace)
if ! grep -q "postactivate" "$ACTIVATE_PATH"; then
  echo "🔧 Přidávám volání postactivate do activate skriptu..."
  echo -e '\n# Run custom postactivate if present\nif [ -f "$VIRTUAL_ENV/bin/postactivate" ]; then\n  source "$VIRTUAL_ENV/bin/postactivate"\nfi' >> "$ACTIVATE_PATH"
fi


# Finální echo
echo "🐍 Aktivní Python: $(which python3)"
echo "✅ Hotovo! Virtuální prostředí je aktivní. Pokračuj v tomto terminálu."
import os
import sys

# Garante que o diretório base está no PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

try:
    from app.core.config import settings
    from app.database import engine
    from sqlalchemy import text

    print("\n" + "=" * 50)
    print("🧪 TESTE DE CONEXÃO - ERP SQL SERVER")
    print("=" * 50)
    print(f"📍 Servidor: {settings.DB_SERVER}")
    print(f"📂 Banco:    {settings.DB_DATABASE}")
    print(f"👤 Usuário:  {settings.DB_USERNAME}")

    is_odbc = "ODBC" in settings.DB_DRIVER
    print(f"⚙️  Driver:   {'pyodbc (ODBC)' if is_odbc else 'pymssql (Direto)'}")
    print(f"🔗 String:   {settings.DATABASE_URL.split('@')[0]}@***")
    print("-" * 50)

    print("🔄 Tentando conectar...")

    # Tenta conectar e executar um comando simples
    with engine.connect() as connection:
        # Definindo um timeout curto para o teste
        result = connection.execute(text("SELECT @@VERSION"))
        version = result.fetchone()[0]
        print("\n✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
        print(f"🖥️  Versão do SQL Server:\n{version}")

except ImportError as ie:
    print(f"\n❌ ERRO DE IMPORTAÇÃO: {ie}")
    print(
        "Certifique-se de que as dependências estão instaladas: pip install -r requirements.txt"
    )
except Exception as e:
    print("\n❌ FALHA NA CONEXÃO:")
    print(f"Erro: {type(e).__name__}")
    print(f"Detalhes: {str(e)}")

    if "ODBC Driver" in str(e):
        print("\n💡 DICA: O driver ODBC especificado não foi encontrado no sistema.")
    elif "Login failed" in str(e):
        print("\n💡 DICA: Credenciais (usuário/senha) inválidas.")
    elif "timeout" in str(e).lower():
        print(
            "\n💡 DICA: Tempo limite esgotado. Verifique o IP/Porta e se o firewall permite a conexão."
        )

print("=" * 50 + "\n")

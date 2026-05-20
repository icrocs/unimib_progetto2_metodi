import sys
from CLI import run_cli

def main():
    if len(sys.argv) == 1:
        print("Avvio in modalità GUI (Interfaccia Grafica)...")
        from gui import run_app
        run_app(img_path="", F=0, d=0)
        
    else:
        print("Avvio in modalità CLI (Terminale)...")
        run_cli()

if __name__ == "__main__":
    main()
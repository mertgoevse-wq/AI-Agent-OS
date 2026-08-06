import sys
import argparse
from scripts.omni_marketplace_importer import OmniMarketplaceImporter

def main():
    parser = argparse.ArgumentParser(description="OMNI-Agent-OS CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import resources into OMNI Library")
    import_parser.add_argument("source", choices=["github"], help="Source of the import (e.g., github)")
    import_parser.add_argument("url", help="URL of the repository to import")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a universal /omni command")
    run_parser.add_argument("command_string", help='The command string (e.g., "/omni build Create SaaS application")')
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search the OMNI marketplace catalog")
    search_parser.add_argument("query", help="Search query")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a package from the catalog")
    install_parser.add_argument("category", help="Category (e.g., agents, skills, prompts)")
    install_parser.add_argument("name", help="Package ID/Name to install")

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a package")
    uninstall_parser.add_argument("category", help="Category (e.g., agents, skills, prompts)")
    uninstall_parser.add_argument("name", help="Package ID/Name to uninstall")
    
    args = parser.parse_args()
    
    if args.command == "import":
        if args.source == "github":
            importer = OmniMarketplaceImporter()
            importer.import_from_github(args.url)
    elif args.command == "run":
        from src.core.omni_command import OmniCommand
        cmd = OmniCommand()
        result = cmd.parse_and_execute(args.command_string)
        print(result)
    elif args.command == "search":
        from src.core.marketplace_catalog import MarketplaceCatalog
        catalog = MarketplaceCatalog()
        res = catalog.search(args.query)
        print(json.dumps(res, indent=2))
    elif args.command == "install":
        from src.core.marketplace_catalog import MarketplaceCatalog
        catalog = MarketplaceCatalog()
        catalog.install(args.category, args.name)
    elif args.command == "uninstall":
        from src.core.marketplace_catalog import MarketplaceCatalog
        catalog = MarketplaceCatalog()
        catalog.uninstall(args.category, args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

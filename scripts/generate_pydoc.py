"""
Script to generate pydoc documentation for the wqu package.
This will create HTML documentation for all modules in the package.
"""
import os
import pydoc
import importlib
import pkgutil

def generate_docs(package_name, output_dir='docs/pydoc'):
    """
    Generate pydoc HTML documentation for a package and its submodules.
    
    Args:
        package_name: The name of the package to document
        output_dir: Directory where HTML files will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Import the package
    package = importlib.import_module(package_name)
    
    # Generate documentation for the package itself
    pydoc.writedoc(package)
    
    # Move the generated HTML file to the output directory
    html_file = f"{package_name}.html"
    if os.path.exists(html_file):
        os.rename(html_file, os.path.join(output_dir, html_file))
    
    # Generate documentation for all submodules
    for _, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
        try:
            module = importlib.import_module(name)
            pydoc.writedoc(module)
            
            # Move the generated HTML file to the output directory
            html_file = f"{name}.html"
            if os.path.exists(html_file):
                os.rename(html_file, os.path.join(output_dir, html_file))
            
            # If it's a subpackage, recursively document its modules
            if ispkg:
                generate_docs(name, output_dir)
        except Exception as e:
            print(f"Error documenting {name}: {e}")

if __name__ == "__main__":
    # Make sure the package is in the Python path
    import sys
    sys.path.insert(0, 'src')
    
    # Generate documentation
    generate_docs('wqu')
    
    print("Documentation generated in docs/pydoc directory")
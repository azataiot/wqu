"""
Script to enhance pydoc-generated HTML files with MathJax support for LaTeX rendering.
This script adds MathJax JavaScript to all HTML files in the specified directory.
"""
import os
import re

def add_mathjax_to_html(html_dir='docs/pydoc'):
    """
    Add MathJax support to all HTML files in the specified directory.
    
    Args:
        html_dir: Directory containing pydoc-generated HTML files
    """
    # MathJax configuration to be added to the HTML head
    mathjax_script = """
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
  }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
"""
    
    # Count of files processed
    count = 0
    
    # Process all HTML files in the directory
    for filename in os.listdir(html_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(html_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Check if MathJax is already added
            if 'mathjax' in content.lower():
                print(f"MathJax already present in {filename}")
                continue
            
            # Add MathJax script before the closing head tag
            if '</head>' in content:
                modified_content = content.replace('</head>', f'{mathjax_script}</head>')
                
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(modified_content)
                
                count += 1
                print(f"Added MathJax to {filename}")
            else:
                print(f"Could not find </head> tag in {filename}")
    
    print(f"\nEnhanced {count} HTML files with MathJax support")
    print("LaTeX expressions in the documentation should now render properly")

if __name__ == "__main__":
    add_mathjax_to_html()
    
    print("\nUsage instructions:")
    print("1. First generate pydoc documentation using generate_pydoc.py")
    print("2. Then run this script to add MathJax support")
    print("3. Open the HTML files in a browser to see properly rendered LaTeX")
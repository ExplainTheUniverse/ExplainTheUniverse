#!/bin/bash

echo "Running Finclude.py..."
python3 Finclude.py

echo "Running BuildPages.py..."
python3 BuildPages.py

echo "Running GeneratePostsList.py..."
python3 Site/blog/GeneratePostsList.py

echo "Running BuildResults.py..."
python3 BuildResults.py

echo "Running BuildBlog.py..."
python3 BuildBlog.py

echo "Both scripts have been executed."
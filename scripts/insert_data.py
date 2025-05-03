#!/usr/bin/env python3
"""
Script to import sample data from CSV files into MongoDB.
"""

import csv
import os
import sys
from pathlib import Path

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from app.database import db


def load_csv(filepath: str):
    """
    Read a CSV file and return a list of dictionaries,
    converting order_id, total_amount and rating to their correct types.
    
    Args:
        filepath (str): Path to the CSV file
        
    Returns:
        list: List of dictionaries with the CSV data
    """
    registros = []
    try:
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields:
                row['order_id'] = int(row['order_id'])
                row['total_amount'] = float(row['total_amount'])
                row['rating'] = int(row['rating'])
                registros.append(row)
        return registros
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {filepath}")
        return []
    except Exception as e:
        print(f"❌ Error al leer el CSV: {e}")
        return []


def insert_orders(data, collection_name='orders'):
    """
    Insert data into the specified MongoDB collection.
    
    Args:
        data (list): List of dictionaries to insert
        collection_name (str): Name of the collection to insert into
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not data:
        print("⚠️ No hay datos para insertar.")
        return False
    
    try:
        collection = db[collection_name]
        result = collection.insert_many(data)
        print(f"✅ Insertados {len(result.inserted_ids)} documentos en '{collection_name}'")
        return True
    except Exception as e:
        print(f"❌ Error durante la inserción: {e}")
        return False


def main():
    """Main function to run the script."""
    # Default CSV location (relative to the script)
    default_csv = os.path.join(project_root, "data", "orders.csv")
    
    # If CSV path is provided as an argument, use it
    csv_path = sys.argv[1] if len(sys.argv) > 1 else default_csv
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"🔍 Buscando archivo CSV en: {csv_path}")
    
    # Load and insert data
    data = load_csv(csv_path)
    if data:
        insert_orders(data)


if __name__ == "__main__":
    main() 
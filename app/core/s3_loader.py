import boto3
import pandas as pd
import json
import os
from typing import List, Dict, Any
from io import StringIO
from botocore.exceptions import NoCredentialsError, ClientError

class S3ProductLoader:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'az-scrapped-data'
        self.prefix = '20k/multi/'
        self.products = []
        self.total_products = 0
    
    def load_products_from_s3(self) -> List[Dict[str, Any]]:
        """Load all products from S3 CSV files"""
        try:
            print("🔄 Connecting to S3...")
            
            # List all CSV files in the bucket
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.prefix
            )
            
            csv_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.csv')]
            print(f"📁 Found {len(csv_files)} CSV files in S3")
            
            all_products = []
            
            for i, csv_key in enumerate(csv_files, 1):
                print(f"📄 Loading file {i}/{len(csv_files)}: {csv_key}")
                
                try:
                    # Download CSV content
                    csv_obj = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=csv_key
                    )
                    
                    # Read CSV
                    csv_content = csv_obj['Body'].read().decode('utf-8')
                    df = pd.read_csv(StringIO(csv_content))
                    
                    # Convert to list of dicts
                    products = df.to_dict('records')
                    all_products.extend(products)
                    
                    print(f"✅ Loaded {len(products)} products from {csv_key}")
                    
                except Exception as e:
                    print(f"⚠️ Error loading {csv_key}: {e}")
                    continue
            
            self.total_products = len(all_products)
            print(f"🎉 Successfully loaded {self.total_products} products from S3!")
            return all_products
            
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure AWS CLI or set environment variables.")
            return []
        except ClientError as e:
            print(f"❌ S3 error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error loading products from S3: {e}")
            return []
    
    def get_products(self) -> List[Dict[str, Any]]:
        """Get products (lazy loading)"""
        if not self.products:
            self.products = self.load_products_from_s3()
        return self.products
    
    def get_total_count(self) -> int:
        """Get total number of products"""
        if self.total_products == 0:
            self.get_products()
        return self.total_products

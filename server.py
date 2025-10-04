import json
import subprocess
import sys
from typing import Optional, Dict, Any

def search_pet(natural_query: str, skip: int = 0, top: int = 100, openai_model: str = "gpt-4o-mini") -> dict:
    """
    Search for pets in FileMaker via OData with pagination support.
    
    Args:
        natural_query: Natural language search query (e.g., "find all espèce = chat")
        skip: Number of records to skip (OData $skip, default: 0)
        top: Maximum records to return (OData $top, default: 100, max: 500)
        openai_model: OpenAI model to use for keyword extraction
    
    Returns:
        dict: FileMaker OData response with pagination info and helper methods
    """
    
    # Validate pagination parameters
    if top > 500:
        top = 500
        print(f"Warning: top value capped at 500 (maximum allowed)")
    
    if skip < 0:
        skip = 0
    
    # Step 1: Use OpenAI to extract search parameters
    openai_prompt = f"""
    Extract the search field and value from this query and return ONLY valid JSON with this exact structure:
    {{"field": "fieldname", "value": "searchvalue"}}
    
    Common field mappings:
    - "espèce" or "species" → "patient_Specie"
    - "nom" or "name" → "description_nom"
    - "race" or "breed" → "description_race"
    - "propriétaire" or "owner" → use related field like "patient.proprietaire.IDP::D_nom"
    
    Query: {natural_query}
    
    Return ONLY the JSON object, no markdown, no explanation.
    """
    
    # Call OpenAI via subprocess (using existing approach)
    openai_command = [
        "python3", "-c",
        f"""
import openai
import json
import os

response = openai.ChatCompletion.create(
    model="{openai_model}",
    messages=[
        {{"role": "system", "content": "You extract search parameters and return only valid JSON."}},
        {{"role": "user", "content": '''{openai_prompt}'''}}
    ],
    temperature=0.0
)

print(response.choices[0].message.content)
"""
    ]
    
    try:
        openai_result = subprocess.run(
            openai_command,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Clean the response (remove markdown code blocks if present)
        openai_response = openai_result.stdout.strip()
        if openai_response.startswith("```json"):
            openai_response = openai_response.split("```json")[1].split("```")[0].strip()
        elif openai_response.startswith("```"):
            openai_response = openai_response.split("```")[1].split("```")[0].strip()
        
        search_params = json.loads(openai_response)
        
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        return {
            "error": f"Failed to extract search parameters: {str(e)}",
            "openai_output": openai_result.stdout if 'openai_result' in locals() else "No output"
        }
    
    # Step 2: Build OData URL with pagination
    # Note: You'll need to replace these with your actual FileMaker server details
    FILEMAKER_SERVER = "your-filemaker-server.com"
    DATABASE_NAME = "DIGIMIDI_DEV"
    TABLE_NAME = "PATIENT"
    USERNAME = "your_username"
    PASSWORD = "your_password"
    
    # Build OData filter
    field = search_params.get("field", "patient_Specie")
    value = search_params.get("value", "")
    
    # Construct the curl command for FileMaker OData API
    odata_url = f"https://{FILEMAKER_SERVER}/fmi/odata/v4/{DATABASE_NAME}/{TABLE_NAME}"
    
    # Build query parameters
    filter_clause = f"{field} eq '{value}'"
    
    # Construct full URL with parameters (properly escaped)
    full_url = f"{odata_url}?\\$filter={filter_clause}&\\$top={top}&\\$skip={skip}&\\$orderby=description_number&\\$count=true"
    
    # Step 3: Execute FileMaker OData API call via curl
    curl_command = [
        "curl", "-s", "-X", "GET",
        full_url,
        "-H", "Content-Type: application/json",
        "-u", f"{USERNAME}:{PASSWORD}"
    ]
    
    try:
        curl_result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the OData response
        odata_response = json.loads(curl_result.stdout)
        
        # Extract pagination info
        total_count = odata_response.get("@odata.count", 0)
        returned_records = len(odata_response.get("value", []))
        has_more = (skip + top) < total_count
        next_skip = skip + top if has_more else None
        
        # Calculate pagination details
        current_page = (skip // top) + 1
        total_pages = (total_count + top - 1) // top  # Ceiling division
        
        # Calculate record range for current page
        start_record = skip + 1
        end_record = min(skip + returned_records, total_count)
        
        # Format response with enhanced pagination info
        result = {
            "response": {
                "dataInfo": {
                    "database": DATABASE_NAME,
                    "table": TABLE_NAME,
                    "totalRecordCount": total_count,
                    "foundCount": total_count,
                    "returnedCount": returned_records,
                    "recordRange": f"{start_record}-{end_record} of {total_count}",
                    "currentPage": current_page,
                    "totalPages": total_pages,
                    "pageSize": top,
                    "offset": skip,
                    "hasMore": has_more,
                    "nextSkip": next_skip,
                    "searchCriteria": {
                        "field": field,
                        "value": value,
                        "originalQuery": natural_query
                    }
                },
                "data": odata_response.get("value", []),
                "pagination": {
                    "summary": f"Page {current_page}/{total_pages} - Records {start_record}-{end_record} of {total_count}",
                    "hasNextPage": has_more,
                    "hasPreviousPage": skip > 0,
                    "nextPageParams": {
                        "skip": next_skip,
                        "top": top
                    } if has_more else None,
                    "previousPageParams": {
                        "skip": max(0, skip - top),
                        "top": top
                    } if skip > 0 else None,
                    "firstPageParams": {
                        "skip": 0,
                        "top": top
                    },
                    "lastPageParams": {
                        "skip": max(0, (total_pages - 1) * top),
                        "top": top
                    }
                }
            }
        }
        
        # Add nextLink if provided by OData
        if "@odata.nextLink" in odata_response:
            result["response"]["dataInfo"]["nextLink"] = odata_response["@odata.nextLink"]
        
        # Add helper message for Claude
        if has_more:
            result["response"]["helper_message"] = (
                f"Retrieved records {start_record}-{end_record} of {total_count}. "
                f"To get the next page, use: search_pet(\"{natural_query}\", skip={next_skip}, top={top})"
            )
        else:
            result["response"]["helper_message"] = f"Retrieved all {returned_records} records (complete result set)."
        
        return result
        
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        return {
            "error": f"FileMaker OData API call failed: {str(e)}",
            "curl_output": curl_result.stdout if 'curl_result' in locals() else "No output",
            "command": " ".join(curl_command)
        }


def get_all_records(natural_query: str, batch_size: int = 100, max_records: int = None) -> dict:
    """
    Helper function to retrieve all records for a query in batches.
    
    Args:
        natural_query: Natural language search query
        batch_size: Number of records per batch (default: 100)
        max_records: Maximum total records to retrieve (default: None for all)
    
    Returns:
        dict: Combined results from all pages
    """
    all_records = []
    skip = 0
    total_retrieved = 0
    
    while True:
        # Calculate how many records to get in this batch
        if max_records:
            remaining = max_records - total_retrieved
            if remaining <= 0:
                break
            current_top = min(batch_size, remaining)
        else:
            current_top = batch_size
        
        # Fetch current page
        result = search_pet(natural_query, skip=skip, top=current_top)
        
        if "error" in result:
            return result
        
        # Extract data
        page_data = result.get("response", {}).get("data", [])
        all_records.extend(page_data)
        
        # Update counters
        total_retrieved += len(page_data)
        
        # Check if we have more pages
        has_more = result.get("response", {}).get("dataInfo", {}).get("hasMore", False)
        if not has_more or (max_records and total_retrieved >= max_records):
            break
        
        # Move to next page
        skip = result.get("response", {}).get("dataInfo", {}).get("nextSkip", skip + batch_size)
    
    # Return combined result
    return {
        "response": {
            "dataInfo": {
                "totalRecordsRetrieved": len(all_records),
                "query": natural_query,
                "batchSize": batch_size
            },
            "data": all_records
        }
    }


# Test function with enhanced output
if __name__ == "__main__":
    print("=== Testing Pagination ===\n")
    
    # Test Page 1
    print("Page 1 - First 100 records:")
    result1 = search_pet("find all espèce = chat", skip=0, top=100)
    if "error" not in result1:
        pagination_info = result1.get("response", {}).get("pagination", {})
        print(f"  {pagination_info.get('summary', 'No summary available')}")
        print(f"  Helper: {result1.get('response', {}).get('helper_message', '')}")
    else:
        print(f"  Error: {result1.get('error')}")
    
    print("\nPage 2 - Records 101-200:")
    result2 = search_pet("find all espèce = chat", skip=100, top=100)
    if "error" not in result2:
        pagination_info = result2.get("response", {}).get("pagination", {})
        print(f"  {pagination_info.get('summary', 'No summary available')}")
        print(f"  Helper: {result2.get('response', {}).get('helper_message', '')}")
    else:
        print(f"  Error: {result2.get('error')}")
    
    print("\n=== Testing get_all_records ===")
    print("Fetching all records in batches of 50, max 150:")
    all_results = get_all_records("find all espèce = chat", batch_size=50, max_records=150)
    if "error" not in all_results:
        print(f"  Total retrieved: {all_results.get('response', {}).get('dataInfo', {}).get('totalRecordsRetrieved', 0)}")
    else:
        print(f"  Error: {all_results.get('error')}")
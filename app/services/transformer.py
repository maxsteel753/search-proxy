

def transform_API_data(data, page, page_size):
    try:
        final_result = {
            "results": [],
            "related_queries": [],
            "page": page,
            "total_results": 0,
            "total_pages": 0
        }

        if data:
            # print(data)
            # Calculate indices for slicing results
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Extract results and related searches
            final_result["results"] = data["results"][start_index:end_index]
            final_result["related_queries"] = data["related_searches"][( int(page) - 1) * 6 : int(page) * 6]
            
            # Calculate total pages
            total_results = len(data["results"])
            final_result["total_results"] = total_results
            final_result["total_pages"] = (total_results + page_size - 1) // page_size  # Round up

        return final_result
    except Exception as e:
        
        return {"error": str(e)}



        
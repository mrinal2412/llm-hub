// webv2/api/searchApis.ts

/**
 * Selects a category based on the user's query and returns related services.
 * 
 * 
 * Sample request:
 curl -X 'GET' \
  'http://localhost:8000/providers?user_query=ipl%202024' \
  -H 'accept: application/json'

 * Sample response:
{"providers": ["ESPNcricinfo", "Hotstar", "Cricbuzz", "YouTube", "Twitter", "Facebook"]}

 * 
 * @param userQuery The query input by the user.
 * @returns An object containing an array of providers related to the query.
 */
export async function getProviders(
  userQuery: string
): Promise<{ providers: string[] }> {
  // Define the endpoint URL
  const url = process.env.NEXT_PUBLIC_API_URL + "/providers";
  console.log("Getting providers for query: %s from URL: %s", userQuery, url);

  try {
    const response = await fetch(url + "?user_query=" + userQuery, {
      method: "GET",
      headers: {
        Accept: "application/json"
      }
    });

    // Check if the response is not OK (i.e., not in the range of 2xx HTTP status codes)
    if (!response.ok) {
      throw new Error(`Failed to select category: ${response.statusText}`);
    }

    // Parse the JSON response body
    const data = await response.json();
    console.log("Providers data: ", data);
    return data;
  } catch (error) {
    // In case of an error (e.g., network issues, invalid JSON, etc.), rethrow or handle it as appropriate
    throw new Error(`Error in selectCategory: ${error}`);
  }
}

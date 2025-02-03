export type ResponseSources = {
  text: string;
  similarity: number;
  doc_id: string;
  start: number;
  end: number;
};

export type QueryResponse = {
  text: string;
  sources: ResponseSources[];
};

const queryIndex = async (query: string): Promise<QueryResponse> => {
  const queryUrl = new URL('http://localhost:5066/query?text=1');
  queryUrl.searchParams.append('text', query);

  const response = await fetch(queryUrl, {
    mode: 'cors',
  });

  if (!response.ok) {
    return {
      text: "You've made an error in query",
      sources: [],
    };
  }

  const queryResponse = (await response.json()) as QueryResponse;
  return queryResponse;
};

export default queryIndex;

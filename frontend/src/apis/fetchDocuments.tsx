export type Document = {
  id: string;
  text: string;
};

const fetchDocuments = async (): Promise<Document[]> => {
  const response = await fetch('http://localhost:5066//getDocumentsList', {
    mode: 'cors',
  });

  if (!response.ok) {
    return [];
  }

  const documentlist = (await response.json()) as Document[];
  return documentlist;
};

export default fetchDocuments;

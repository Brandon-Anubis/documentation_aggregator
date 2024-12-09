export interface ClipResult {
    id: string;
    title: string;
    url: string;
    markdown_path: string | null;
    pdf_path: string | null;
    timestamp: string;
  }
  
  export interface ListedResult {
    id: string;
    title: string;
    url: string;
    timestamp: string;
  }
  
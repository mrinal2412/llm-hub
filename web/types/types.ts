// webv2/types/types.ts

export interface SearchResultItem {
  title: string;
  description: string;
  // Add other fields here as necessary
}

export interface Task {
  task_id: number;
  title: string;
  description: string;
  status: string;
  notes: string;
  owner: string;
}

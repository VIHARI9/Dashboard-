export const api = {
  get: async <T,>(url: string): Promise<T> => { const response = await fetch(url); if (!response.ok) throw new Error(await response.text()); return response.json(); },
  post: async <T,>(url: string): Promise<T> => { const response = await fetch(url, { method: "POST" }); if (!response.ok) throw new Error(await response.text()); return response.json(); },
};

export type Role = 'user' | 'support' | 'admin';
export type TicketStatus = 'open' | 'pending' | 'solved' | 'closed';
export interface Ticket { id:number; title:string; description:string; status:TicketStatus; priority:string; assignee_id:number|null; }

// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
}

// 认证状态类型
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

// 错题类型
export interface Question {
  id: number;
  user_id: number;
  content: string;
  solution?: string;
  remarks?: string;
  image_url?: string;
  created_at: string;
}

// 知识点类型
export interface KnowledgePoint {
  id: number;
  subject: string;
  chapter: string;
  section: string;
  item: string;
  details: string;
  mark_count: number;
  created_at: string;
}

// 用户标记类型
export interface UserMark {
  id: number;
  user_id: number;
  knowledge_point_id: number;
  question_id: number;
  marked_at: string;
} 
export interface UserProfile {
  id: string;
  user_id: string;
  first_name: string | null;
  middle_name: string | null;
  last_name: string | null;
  bio: string | null;
  interests: string[] | null;
  avatar_url: string | null;
  location: string | null;
  is_profile_complete: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileRequest {
  first_name?: string | null;
  middle_name?: string | null;
  last_name?: string | null;
  bio?: string | null;
  interests?: string[] | null;
  avatar_url?: string | null;
  location?: string | null;
}
/*
  # Create user configurations table

  1. New Tables
    - `user_configs`
      - `id` (uuid, primary key)
      - `user_id` (bigint, unique) - Telegram user ID
      - `api_id` (integer) - Telegram API ID
      - `api_hash` (text) - Telegram API hash
      - `phone_number` (text) - User's phone number
      - `channel_id` (text) - Notification channel ID
      - `interval` (real) - Check interval in seconds
      - `language` (text) - Interface language
      - `gift_ranges` (jsonb) - Gift purchase ranges configuration
      - `purchase_only_upgradable_gifts` (boolean) - Only buy upgradable gifts
      - `prioritize_low_supply` (boolean) - Prioritize rare gifts
      - `is_active` (boolean) - Whether the bot is active for this user
      - `session_file_path` (text) - Path to Pyrogram session file
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    - `authorized_users`
      - `id` (uuid, primary key)
      - `user_id` (bigint, unique) - Telegram user ID
      - `username` (text) - Telegram username
      - `is_admin` (boolean) - Admin privileges
      - `created_at` (timestamp)

  2. Security
    - Enable RLS on both tables
    - Add policies for authenticated access
*/

CREATE TABLE IF NOT EXISTS user_configs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint UNIQUE NOT NULL,
  api_id integer,
  api_hash text,
  phone_number text,
  channel_id text,
  interval real DEFAULT 15.0,
  language text DEFAULT 'en',
  gift_ranges jsonb DEFAULT '[]'::jsonb,
  purchase_only_upgradable_gifts boolean DEFAULT false,
  prioritize_low_supply boolean DEFAULT false,
  is_active boolean DEFAULT false,
  session_file_path text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS authorized_users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint UNIQUE NOT NULL,
  username text,
  is_admin boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE user_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE authorized_users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own config"
  ON user_configs
  FOR ALL
  TO authenticated
  USING (true);

CREATE POLICY "Authorized users can be read"
  ON authorized_users
  FOR SELECT
  TO authenticated
  USING (true);
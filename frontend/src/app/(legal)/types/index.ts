export interface User {
  public_id: string;
  phone_number: string;
  email: string | null;
  first_name: string;
  last_name: string;
  full_name: string;
  tier: 'regular' | 'bronze' | 'silver' | 'gold' | 'platinum';
  kyc_tier: 0 | 1 | 2 | 3;
  referral_code: string;
  phone_verified: boolean;
  email_verified: boolean;
  wallet_balance: string;
  date_joined: string;
}

export interface Wallet {
  public_id: string;
  balance: string;
  status: 'active' | 'frozen' | 'suspended';
  created_at: string;
}

export interface VirtualAccount {
  account_number: string;
  bank_name: string;
  account_name: string;
}

export interface Service {
  public_id: string;
  category: string;
  network: string;
  name: string;
  slug: string;
  description: string;
  display_order: number;
  icon: string;
}

export interface ServiceVariation {
  public_id: string;
  service_name: string;
  network: string;
  name: string;
  variation_type: 'fixed' | 'variable_amount';
  variation_code: string;
  face_value: string | null;
  validity_days: number | null;
  data_mb: number | null;
  display_order: number;
  price: string | null;
}

export interface Transaction {
  public_id: string;
  reference: string;
  transaction_type: string;
  variation_name: string;
  network: string;
  recipient: string;
  amount: string;
  sale_price: string;
  status: 'pending' | 'processing' | 'success' | 'failed' | 'refunded';
  status_message: string;
  created_at: string;
  completed_at: string | null;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}

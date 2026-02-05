CREATE OR REPLACE FUNCTION encrypt_credential(
    plain_text TEXT,
    secret_key TEXT
) RETURNS TEXT AS $$
BEGIN
    -- Use pgp_sym_encrypt from pgcrypto extension
    -- Encrypts data with a symmetric key
    RETURN pgp_sym_encrypt(plain_text, secret_key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

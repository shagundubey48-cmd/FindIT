USE finditplus;

CREATE TABLE IF NOT EXISTS claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claimant_id INT NOT NULL,
    item_id INT NOT NULL,
    ownership_details TEXT NOT NULL,
    proof_type VARCHAR(50) NULL,
    proof_details TEXT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    admin_remarks TEXT NULL,
    status_updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_claim_user
        FOREIGN KEY (claimant_id) REFERENCES users(id),

    CONSTRAINT fk_claim_item
        FOREIGN KEY (item_id) REFERENCES items(id)
);

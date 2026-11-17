
CREATE TABLE IF NOT EXISTS claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claimant_id INT NOT NULL,
    item_id INT NOT NULL,
    ownership_details TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_claim_user
        FOREIGN KEY (claimant_id) REFERENCES users(id),

    CONSTRAINT fk_claim_item
        FOREIGN KEY (item_id) REFERENCES items(id)
);


USE finditplus;

CREATE TABLE IF NOT EXISTS handovers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claim_id INT NOT NULL UNIQUE,
    item_id INT NOT NULL,
    handed_over_by INT NOT NULL,
    received_by INT NOT NULL,
    handover_notes TEXT NULL,
    handed_over_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_handover_claim
        FOREIGN KEY (claim_id) REFERENCES claims(id),

    CONSTRAINT fk_handover_item
        FOREIGN KEY (item_id) REFERENCES items(id),

    CONSTRAINT fk_handover_admin
        FOREIGN KEY (handed_over_by) REFERENCES users(id),

    CONSTRAINT fk_handover_recipient
        FOREIGN KEY (received_by) REFERENCES users(id)
);

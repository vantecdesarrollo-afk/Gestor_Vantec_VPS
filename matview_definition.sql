 SELECT c.uuid,
    c.folio,
    c.total,
    c.rfc_receptor,
    c.entidad_id,
    COALESCE(sum(r.monto_pagado), (0)::numeric) AS total_pagado,
        CASE
            WHEN ((c.total - COALESCE(sum(r.monto_pagado), (0)::numeric)) < 1.00) THEN 0.00
            ELSE (c.total - COALESCE(sum(r.monto_pagado), (0)::numeric))
        END AS saldo_insoluto,
        CASE
            WHEN ((c.total - COALESCE(sum(r.monto_pagado), (0)::numeric)) < 1.00) THEN 'PAGADO'::text
            WHEN (COALESCE(sum(r.monto_pagado), (0)::numeric) <= (0)::numeric) THEN 'PENDIENTE'::text
            ELSE 'PARCIAL'::text
        END AS estado_semaforo
   FROM (comprobantes c
     LEFT JOIN cfdi_relacionados r ON ((lower((c.uuid)::text) = lower((r.uuid_relacionado)::text))))
  WHERE (((c.metodo_pago)::text = 'PPD'::text) AND ((c.tipo_comprobante)::text = 'I'::text))
  GROUP BY c.uuid, c.folio, c.total, c.rfc_receptor, c.entidad_id;
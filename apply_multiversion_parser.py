file_path = "src/services/cfdi_processor.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update _parse_cfdi_deep Pagos parsing (lines 274 - 294 approximate)
target_pagos = """        pago20_ns = {'pago20': 'http://www.sat.gob.mx/Pagos20'}
        pagos_node = root.find('.//pago20:Pagos', pago20_ns)
        monto_total_pagos = None
        
        if pagos_node is not None:
            # Vantec Smart Control: Extraer Monto Real de Totales Pago 2.0
            totales_node = pagos_node.find('pago20:Totales', pago20_ns)
            if totales_node is not None:
                monto_total_pagos = totales_node.get('MontoTotalPagos')
                logger.info(f"💰 Vantec Intelligence: MontoTotalPagos extraído: {monto_total_pagos}")

            for pago in pagos_node.findall('pago20:Pago', pago20_ns):
                for doc_rel in pago.findall('pago20:DoctoRelacionado', pago20_ns):
                    relaciones.append({
                        "uuid_relacionado": doc_rel.get('IdDocumento'),
                        "tipo_relacion": "PAGO",
                        "monto_pagado": float(doc_rel.get('ImpPagado') or 0),
                        "saldo_insoluto": float(doc_rel.get('ImpSaldoInsoluto') or 0),
                        "num_parcialidad": int(doc_rel.get('NumParcialidad') or 1)
                    })"""

replacement_pagos = """        # Vantec Multiversion: Complemento de Pagos 1.0 & 2.0 con XPath Wildcard
        pagos_node = root.find('.//{*}Pagos')
        monto_total_pagos = None
        
        if pagos_node is not None:
            # 1. Totales (Solo en Pago 2.0)
            totales_node = pagos_node.find('{*}Totales')
            if totales_node is not None:
                monto_total_pagos = totales_node.get('MontoTotalPagos')
                logger.info(f"💰 Vantec Intelligence: MontoTotalPagos extraído: {monto_total_pagos}")

            # 2. Iterar Pagos (V1.0 & V2.0)
            for pago in pagos_node.findall('{*}Pago'):
                for doc_rel in pago.findall('{*}DoctoRelacionado'):
                    relaciones.append({
                        "uuid_relacionado": doc_rel.get('IdDocumento'),
                        "tipo_relacion": "PAGO",
                        "monto_pagado": float(doc_rel.get('ImpPagado') or doc_rel.get('ImpPagado') or 0),
                        "saldo_insoluto": float(doc_rel.get('ImpSaldoInsoluto') or 0),
                        "num_parcialidad": int(doc_rel.get('NumParcialidad') or 1)
                    })"""

# 2. Update _extraer_parent_uuid_de_pago (lines 350-352 approximate)
target_parent = """        namespaces = {'pago20': 'http://www.sat.gob.mx/Pagos20'}
        docto_relacionado = root.find('.//pago20:DoctoRelacionado', namespaces)
        return docto_relacionado.get('IdDocumento') if docto_relacionado is not None else None"""

replacement_parent = """        docto_relacionado = root.find('.//{*}DoctoRelacionado')
        return docto_relacionado.get('IdDocumento') if docto_relacionado is not None else None"""

if target_pagos in content and target_parent in content:
    content = content.replace(target_pagos, replacement_pagos)
    content = content.replace(target_parent, replacement_parent)
    print("✅ CfdiProcessor updated with XPath wildcards.")
else:
    target_pagos_crlf = target_pagos.replace('\n', '\r\n')
    replacement_pagos_crlf = replacement_pagos.replace('\n', '\r\n')
    target_parent_crlf = target_parent.replace('\n', '\r\n')
    replacement_parent_crlf = replacement_parent.replace('\n', '\r\n')
    if target_pagos_crlf in content and target_parent_crlf in content:
        content = content.replace(target_pagos_crlf, replacement_pagos_crlf)
        content = content.replace(target_parent_crlf, replacement_parent_crlf)
        print("✅ CfdiProcessor updated with XPath wildcards (CRLF).")
    else:
        print("❌ Targets not found in CfdiProcessor.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

file_path = "src/services/cfdi_processor.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Conceptos
content = content.replace("conceptos_node = root.find('.//cfdi:Conceptos', namespaces)", "conceptos_node = root.find('.//{*}Conceptos')")
content = content.replace("for c in conceptos_node.findall('cfdi:Concepto', namespaces):", "for c in conceptos_node.findall('{*}Concepto'):")

# 2. Update CfdiRelacionados
content = content.replace("cfdi_rel_node = root.find('.//cfdi:CfdiRelacionados', namespaces)", "cfdi_rel_node = root.find('.//{*}CfdiRelacionados')")
content = content.replace("for rel in cfdi_rel_node.findall('cfdi:CfdiRelacionado', namespaces):", "for rel in cfdi_rel_node.findall('{*}CfdiRelacionado'):")

# 3. Update Emisor / Receptor
content = content.replace("emisor = root.find('.//cfdi:Emisor', namespaces)", "emisor = root.find('.//{*}Emisor')")
content = content.replace("receptor = root.find('.//cfdi:Receptor', namespaces)", "receptor = root.find('.//{*}Receptor')")

# 4. Update Impuestos
content = content.replace("impuestos_node = root.find('.//cfdi:Impuestos', namespaces)", "impuestos_node = root.find('.//{*}Impuestos')")

# 5. Type normalization fix inside _parse_cfdi_deep (V2.0 was sum(r), we want v1.0 sum to work!)
# Since I already updated the loop, it already loads into relaciones.
print("✅ CfdiProcessor heavily patched with wildcards.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.utils import timezone


def gerar_pdf_os(orcamento):
    """Gera PDF da Ordem de Serviço"""
    buffer = BytesIO()

    # Configurar o documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=10*mm,
        bottomMargin=10*mm
    )

    # Estilos
    styles = getSampleStyleSheet()

    # Estilos personalizados
    estilo_titulo = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=5,
        alignment=TA_CENTER
    )

    estilo_subtitulo = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=5,
        alignment=TA_LEFT
    )

    estilo_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=3
    )

    estilo_destaque = ParagraphStyle(
        'CustomDestaque',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#c0392b'),
        spaceAfter=3,
        fontWeight='bold'
    )

    # Conteúdo do PDF
    story = []

    # Cabeçalho
    story.append(Paragraph("NAYA PERSONALIZADOS", estilo_titulo))

    # Linha divisória
    story.append(Spacer(1, 2*mm))
    story.append(Table(
        [['']],
        colWidths=[150*mm],
        style=[('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#3498db'))]
    ))
    story.append(Spacer(1, 2*mm))

    # Informações da OS
    info_os_data = [
        [Paragraph("<b>Nº OS:</b>", estilo_normal),
         Paragraph(f"<b>{orcamento.numero_os}</b>", estilo_destaque)],
        [Paragraph("<b>Data Emissão:</b>", estilo_normal),
         Paragraph(timezone.now().strftime("%d/%m/%Y %H:%M"), estilo_normal)],
    ]

    info_os_table = Table(info_os_data, colWidths=[40*mm, 110*mm])
    info_os_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    story.append(info_os_table)
    story.append(Spacer(1, 3*mm))

    # Dados do Cliente
    story.append(Paragraph("DADOS DO CLIENTE", estilo_subtitulo))
    story.append(Table([['']], colWidths=[150*mm],
                 style=[('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.append(Spacer(1, 2*mm))

    cliente_data = [
        [
            Paragraph("<b>Nome:</b>", estilo_normal), Paragraph(
                orcamento.cliente.get_full_name() or orcamento.cliente.username,
                estilo_normal)
        ],
        [
            Paragraph("<b>Email:</b>", estilo_normal),
            Paragraph(orcamento.cliente.email, estilo_normal)
        ],
    ]

    if hasattr(orcamento.cliente, 'profile') and orcamento.cliente.profile:
        profile = orcamento.cliente.profile
        if profile.cpf:
            cliente_data.append(
                [
                    Paragraph("<b>CPF:</b>", estilo_normal),
                    Paragraph(profile.cpf, estilo_normal)
                ]
            )
        if profile.logradouro:
            endereco = f"{profile.logradouro}, {profile.numero}"
            if profile.complemento:
                endereco += f" - {profile.complemento}"
            endereco += f"<br/>{profile.bairro} - {profile.cidade}"
            if profile.state:
                endereco += f"/{profile.state}"
            if profile.cep:
                endereco += f"<br/>CEP: {profile.cep}"
            cliente_data.append(
                [
                    Paragraph("<b>Endereço:</b>", estilo_normal),
                    Paragraph(endereco, estilo_normal)
                ]
            )

    cliente_table = Table(cliente_data, colWidths=[30*mm, 120*mm])
    cliente_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    story.append(cliente_table)
    story.append(Spacer(1, 3*mm))

    # Informações do Serviço
    story.append(Paragraph("INFORMAÇÕES DO SERVIÇO", estilo_subtitulo))
    story.append(Table([['']], colWidths=[150*mm],
                 style=[('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.append(Spacer(1, 3*mm))

    servico_data = [
        [Paragraph("<b>Data Orçamento:</b>", estilo_normal),
         Paragraph(orcamento.data_criacao.strftime("%d/%m/%Y %H:%M"),
                   estilo_normal
                   )],
        [Paragraph("<b>Data Máxima Entrega:</b>", estilo_normal),
         Paragraph(orcamento.data_maxima_entrega.strftime("%d/%m/%Y"),
                   estilo_normal
                   )],
    ]

    if orcamento.data_prevista_entrega:
        servico_data.append([
            Paragraph("<b>Data Prevista:</b>", estilo_normal),
            Paragraph(
                orcamento.data_prevista_entrega.strftime("%d/%m/%Y"),
                estilo_normal
            )])

    servico_data.append([
        Paragraph("<b>Valor Total:</b>", estilo_normal),
        Paragraph(f"R$ {orcamento.get_valor_final():.2f}", estilo_destaque)])

    if orcamento.data_inicio_producao:
        servico_data.append([Paragraph(
            "<b>Início Produção:</b>", estilo_normal),
            Paragraph(
                orcamento.data_inicio_producao.strftime("%d/%m/%Y %H:%M"),
            estilo_normal)])

    if orcamento.data_conclusao_producao:
        servico_data.append([Paragraph(
            "<b>Conclusão:</b>", estilo_normal), Paragraph(
            orcamento.data_conclusao_producao.strftime(
                "%d/%m/%Y %H:%M"),
                estilo_normal
        )])

    servico_table = Table(servico_data, colWidths=[45*mm, 105*mm])
    servico_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    story.append(servico_table)
    story.append(Spacer(1, 3*mm))

    # Itens da OS
    story.append(Paragraph("ITENS PARA PRODUÇÃO", estilo_subtitulo))
    story.append(Table([['']], colWidths=[150*mm],
                 style=[('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.append(Spacer(1, 2*mm))

    for i, item in enumerate(orcamento.itens.all(), 1):
        story.append(
            Paragraph(f"<b>Item {i}: {item.produto.name}</b>", estilo_normal))

        item_data = [
            [Paragraph("<b>Quantidade:</b>", estilo_normal),
             Paragraph(str(item.quantidade), estilo_normal)],
            [Paragraph("<b>Personalização:</b>", estilo_normal),
             Paragraph(
                item.descricao_personalizacao or "Não informada",
                estilo_normal)
             ],
        ]

        if item.preco_unitario and item.preco_unitario > 0:
            item_data.append([
                Paragraph("<b>Preço Unitário:</b>",
                          estilo_normal),
                Paragraph(f"R$ {item.preco_unitario:.2f}",
                          estilo_normal)
            ])
            item_data.append([
                Paragraph("<b>Total Item:</b>", estilo_normal),
                Paragraph(f"R$ {item.preco_total:.2f}",
                          estilo_destaque)
            ])

        item_table = Table(item_data, colWidths=[35*mm, 115*mm])
        item_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        story.append(item_table)
        story.append(Spacer(1, 5*mm))

    # Observações
    if orcamento.observacoes_cliente or orcamento.observacoes_empresa or orcamento.observacoes_producao:
        story.append(Paragraph("OBSERVAÇÕES", estilo_subtitulo))
        story.append(Table([['']], colWidths=[
                     150*mm], style=[('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey)]))
        story.append(Spacer(1, 2*mm))

        if orcamento.observacoes_cliente:
            story.append(Paragraph("<b>Cliente:</b>", estilo_normal))
            story.append(
                Paragraph(orcamento.observacoes_cliente, estilo_normal))
            story.append(Spacer(1, 3*mm))

        if orcamento.observacoes_empresa:
            story.append(Paragraph("<b>Empresa:</b>", estilo_normal))
            story.append(
                Paragraph(orcamento.observacoes_empresa, estilo_normal))
            story.append(Spacer(1, 3*mm))

        if orcamento.observacoes_producao:
            story.append(Paragraph("<b>Produção:</b>", estilo_normal))
            story.append(
                Paragraph(orcamento.observacoes_producao, estilo_normal))

    # Assinaturas
    story.append(Spacer(1, 15*mm))
    assinaturas_data = [
        [Paragraph("__________________________________", estilo_normal),
         Paragraph("__________________________________", estilo_normal)
         ],
        [Paragraph("Responsável pela Produção", estilo_normal),
         Paragraph("Conferência/Qualidade", estilo_normal)
         ],
        [Paragraph("Naya Personalizados", estilo_normal),
         Paragraph("Naya Personalizados", estilo_normal)
         ],
    ]

    assinaturas_table = Table(assinaturas_data, colWidths=[75*mm, 75*mm])
    assinaturas_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    story.append(assinaturas_table)

    # Rodapé
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph(
        f"Documento gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')} - Sistema Naya Personalizados",
        ParagraphStyle(
            'Rodape', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))

    # Gerar PDF
    doc.build(story)

    buffer.seek(0)
    return buffer

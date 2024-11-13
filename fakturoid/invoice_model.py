from django.db import models
from decimal import Decimal
from django.utils.translation import gettext_lazy as _


class AbstractInvoice(models.Model):
    # Identification and Document Details
    custom_id = models.CharField(_("Custom ID"), max_length=255, blank=True, null=True)
    document_type = models.CharField(
        _("Document Type"),
        max_length=50,
        choices=[
            ('partial_proforma', 'Partial Proforma'),
            ('proforma', 'Proforma'),
            ('correction', 'Correction'),
            ('tax_document', 'Tax Document'),
            ('final_invoice', 'Final Invoice'),
            ('invoice', 'Invoice'),
        ],
    )
    proforma_followup_document = models.CharField(
        _("Proforma Followup Document"),
        max_length=50,
        choices=[
            ('final_invoice_paid', 'Invoice Paid'),
            ('final_invoice', 'Invoice with Edit'),
            ('tax_document', 'Document to Payment'),
            ('none', 'None'),
        ],
        blank=True,
        null=True,
    )
    tax_document_ids = models.JSONField(_("Tax Document IDs"), blank=True, null=True)
    correction_id = models.IntegerField(_("Correction ID"), blank=True, null=True)
    number = models.CharField(_("Number"), max_length=50, blank=True, null=True)
    number_format_id = models.IntegerField(_("Number Format ID"), blank=True, null=True)
    variable_symbol = models.CharField(_("Variable Symbol"), max_length=50, blank=True, null=True)

    # Company Information
    your_name = models.CharField(_("Your Name"), max_length=255, blank=True, null=True)
    your_street = models.CharField(_("Your Street"), max_length=255, blank=True, null=True)
    your_city = models.CharField(_("Your City"), max_length=100, blank=True, null=True)
    your_zip = models.CharField(_("Your ZIP"), max_length=20, blank=True, null=True)
    your_country = models.CharField(_("Your Country"), max_length=2, blank=True, null=True)
    your_registration_no = models.CharField(_("Your Registration No."), max_length=50, blank=True, null=True)
    your_vat_no = models.CharField(_("Your VAT No."), max_length=50, blank=True, null=True)
    your_local_vat_no = models.CharField(_("Your Local VAT No."), max_length=50, blank=True, null=True)

    # Client Information
    client_name = models.CharField(_("Client Name"), max_length=255, blank=True, null=True)
    client_street = models.CharField(_("Client Street"), max_length=255, blank=True, null=True)
    client_city = models.CharField(_("Client City"), max_length=100, blank=True, null=True)
    client_zip = models.CharField(_("Client ZIP"), max_length=20, blank=True, null=True)
    client_country = models.CharField(_("Client Country"), max_length=2, blank=True, null=True)
    client_has_delivery_address = models.BooleanField(_("Client Has Delivery Address"), default=False)
    client_delivery_name = models.CharField(_("Client Delivery Name"), max_length=255, blank=True, null=True)
    client_delivery_street = models.CharField(_("Client Delivery Street"), max_length=255, blank=True, null=True)
    client_delivery_city = models.CharField(_("Client Delivery City"), max_length=100, blank=True, null=True)
    client_delivery_zip = models.CharField(_("Client Delivery ZIP"), max_length=20, blank=True, null=True)
    client_delivery_country = models.CharField(_("Client Delivery Country"), max_length=2, blank=True, null=True)
    client_registration_no = models.CharField(_("Client Registration No."), max_length=50, blank=True, null=True)
    client_vat_no = models.CharField(_("Client VAT No."), max_length=50, blank=True, null=True)

    # Financial Details
    subtotal = models.DecimalField(_("Subtotal (Excl. VAT)"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(_("Total (Incl. VAT)"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    native_subtotal = models.DecimalField(_("Native Subtotal (Excl. VAT)"), max_digits=10, decimal_places=2,
                                          default=Decimal('0.00'))
    native_total = models.DecimalField(_("Native Total (Incl. VAT)"), max_digits=10, decimal_places=2,
                                       default=Decimal('0.00'))
    remaining_amount = models.DecimalField(_("Remaining Amount (Incl. VAT)"), max_digits=10, decimal_places=2,
                                           default=Decimal('0.00'))
    remaining_native_amount = models.DecimalField(_("Remaining Native Amount"), max_digits=10, decimal_places=2,
                                                  default=Decimal('0.00'))

    # Payment Information
    payment_method = models.CharField(
        _("Payment Method"),
        max_length=50,
        choices=[
            ('bank', 'Bank'),
            ('cash', 'Cash'),
            ('cod', 'Cash on Delivery'),
            ('card', 'Card'),
            ('paypal', 'PayPal'),
            ('custom', 'Custom'),
        ],
        blank=True,
        null=True,
    )
    custom_payment_method = models.CharField(_("Custom Payment Method"), max_length=20, blank=True, null=True)
    currency = models.CharField(_("Currency"), max_length=3, blank=True, null=True)
    exchange_rate = models.DecimalField(_("Exchange Rate"), max_digits=10, decimal_places=2, blank=True, null=True)
    iban = models.CharField(_("IBAN"), max_length=34, blank=True, null=True)
    swift_bic = models.CharField(_("SWIFT/BIC"), max_length=11, blank=True, null=True)

    # Status and Timestamps
    status = models.CharField(
        _("Status"),
        max_length=50,
        choices=[
            ("open", "Open"),
            ("sent", "Sent"),
            ("overdue", "Overdue"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
            ("uncollectible", "Uncollectible"),
        ]
    )
    issued_on = models.DateField(_("Issue Date"), blank=True, null=True)
    due = models.IntegerField(_("Due Days"), default=30)
    due_on = models.DateField(_("Due Date"), blank=True, null=True)
    sent_at = models.DateTimeField(_("Sent At"), blank=True, null=True)
    paid_on = models.DateField(_("Paid On"), blank=True, null=True)
    reminder_sent_at = models.DateTimeField(_("Reminder Sent At"), blank=True, null=True)
    cancelled_at = models.DateTimeField(_("Cancelled At"), blank=True, null=True)
    uncollectible_at = models.DateTimeField(_("Uncollectible At"), blank=True, null=True)
    locked_at = models.DateTimeField(_("Locked At"), blank=True, null=True)
    webinvoice_seen_on = models.DateField(_("Webinvoice Seen On"), blank=True, null=True)

    # Notes
    note = models.TextField(_("Note"), blank=True, null=True)
    footer_note = models.TextField(_("Footer Note"), blank=True, null=True)
    private_note = models.TextField(_("Private Note"), blank=True, null=True)
    tags = models.JSONField(_("Tags"), blank=True, null=True)

    # Links and URLs
    html_url = models.URLField(_("HTML URL"), blank=True, null=True)
    public_html_url = models.URLField(_("Public HTML URL"), blank=True, null=True)
    pdf_url = models.URLField(_("PDF URL"), blank=True, null=True)

    # Attachments and Related Objects
    attachments = models.JSONField(_("Attachments"), blank=True, null=True)
    lines = models.JSONField(_("Lines"), blank=True, null=True)
    eet_records = models.JSONField(_("EET Records"), blank=True, null=True)
    vat_rates_summary = models.JSONField(_("VAT Rates Summary"), blank=True, null=True)
    paid_advances = models.JSONField(_("Paid Advances"), blank=True, null=True)
    payments = models.JSONField(_("Payments"), blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        abstract = True
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

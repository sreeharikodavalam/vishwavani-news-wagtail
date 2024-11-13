from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    attribution = blocks.CharBlock(required=False)

    class Meta:
        template = 'news/blocks/quote_block.html'
        icon = 'openquote'


class ContentBlock(blocks.StreamBlock):
    paragraph = blocks.RichTextBlock()
    image = ImageChooserBlock()
    quote = QuoteBlock()
    embed = EmbedBlock()

    class Meta:
        template = 'news/blocks/content_block.html'

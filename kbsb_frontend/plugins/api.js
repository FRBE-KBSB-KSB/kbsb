import Content from '@/api/content'
import Page from '@/api/page'
import Root from '@/api/root'
import File_ from '@/api/file'

export default (context, inject) => {
  const factories = {
    content: Content(context),
    page: Page(context),
    root: Root(context),
    file: File_(context)
  }
  inject('api', factories)
}

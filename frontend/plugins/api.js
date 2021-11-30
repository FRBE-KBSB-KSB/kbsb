import Content from '@/api/content'
import Page from '@/api/page'
import Root from '@/api/root'

export default (context, inject) => {
  const factories = {
    content: Content(context),
    page: Page(context),
    root: Root(context),
  }
  inject('api', factories)
}

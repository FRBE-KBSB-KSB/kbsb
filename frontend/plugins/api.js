import Content from '@/api/content'
import Page from '@/api/page'
import Root from '@/api/root'
import File_ from '@/api/file'
import Club from '@/api/club'
import Old from '@/api/old'
import Interclub from '@/api/interclub'

export default (context, inject) => {
  const factories = {
    content: Content(context),
    page: Page(context),
    root: Root(context),
    file: File_(context),
    club: Club(context),
    old: Old(context),
    interclub: Interclub(context),
  }
  inject('api', factories)
}

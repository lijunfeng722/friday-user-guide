/* Open screenshots at their original size, with a keyboard accessible link. */
function linkScreenshots(){
 for(const image of document.querySelectorAll('.md-content__inner img')){
  image.loading='lazy';image.decoding='async';
  if(image.closest('a'))continue;
  const link=document.createElement('a');link.href=image.src;link.target='_blank';link.rel='noopener';
  link.className='screenshot-link';link.setAttribute('aria-label','查看原图：'+image.alt);link.title='点击查看原尺寸图片';
  image.before(link);link.append(image);
 }
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',linkScreenshots);else linkScreenshots();

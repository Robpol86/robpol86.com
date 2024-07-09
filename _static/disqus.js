var disqus_config; // Accessed by embed.js
const SphinxDisqus = {
    init: function () {
        let disqus_thread = document.getElementById('disqus_thread'); // Disqus <div />
        let disqus_shortname = disqus_thread.getAttribute('data-disqus-shortname');
        let disqus_identifier = disqus_thread.getAttribute('data-disqus-identifier');

        // Disqus universal code below: https://disqus.com/admin/install/platforms/universalcode/
        disqus_config = function () {
            this.page.identifier = disqus_identifier;
        };
        let d = document, s = d.createElement('script');
        s.src = 'https://' + disqus_shortname + '.disqus.com/embed.js';
        s.setAttribute('data-timestamp', +new Date());
        (d.head || d.body).appendChild(s);
    },
};

document.addEventListener('DOMContentLoaded', function () {
    SphinxDisqus.init();
});

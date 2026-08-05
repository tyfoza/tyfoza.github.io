---
title: "typst"
date: 2026-07-01T08:05:00Z
url: "/posts/2026/07/typst/"
aliases:
  - "/2026/07/typst.html"
---

<div class="typst-code">
  #set page(paper: "a4")
 = Kapitola o mezerách

Tento odstavec je první, takže podle pravidel české sazby nemá zarážku. Jeho řádkování je nastaveno tak, aby text dýchal.

Tento druhý odstavec už zarážku má. Díky tomu, že jsme nastavili `spacing` na stejnou hodnotu jako `leading`, je mezera mezi těmito dvěma odstavci opticky naprosto stejná jako mezera mezi řádky uvnitř nich. Písmena už se nebudou překrývat.

Tohle je dobré a má smysl.

\
\
\
$ sigma_y (tau) = sqrt(1/2 (limits(sum)_(i=1)^(N-1) (y_(i+1) - y_i)^2)/(N - 1)) $

$ (limits(sum)_(i=1)^(N-1) (y_(i+1) - y_i)^2)/(N - 1) $
\
\
$ sigma_y² (tau) = 1/2(limits(sum)_(i=1)^(N-1) (y_(i+1) - y_i)^2)/(N - 1) $
\
$ sigma_y (tau) =  sqrt(sigma_y² (tau)) $
\
$ "ADEV" =  sqrt("AVAR") $

\

\
\
\
$1/10=0,1=10%$

</div>
# Sample document

This is a markdown document to illustrate how markdown files can be rendered as RSpace documents.

Markdown is a versatile and easy way to create formatted text. It can include _emphasized_ text as well as __bold__ text. How math text such as $2d\sin\theta=n\lambda$ or
$$\Delta\vec{k}=\vec{g}_{hkl}$$ is displayed on RSpace is not necessarily obvious though. Nevertheless, adding them to the markdown file enables you to get the syntax into the generated document on RSpace, and then you can make required changes there instead.

## Other syntax

### Tables

|Column 1 | Column 2 |
|--------:|:---------|
|0.1|0.2|
|0.3|0.4|
|0.5|0.6|

### Lists

When adding a list, the list must be separated from other text by blank lines! If not, it will __not__ be rendered as a proper list in html.

#### Unordered lists

My unordered lists are: <!-- Remember a blank line before the list! -->

- short
- clear
- obvious
- not helpful

#### Numbered lists

My numbered lists are: <!-- Remember a blank line before the list! -->

1. longer
2. for
3. no
4. particular
5. reason
6. but
7. for
8. this example
9. they 
10. serve a purpose

### Links

You can also add links to markdown. This is the [NTNU RSpace](https://rspace.ntnu.no/workspace) and this is an [internal link](#other-syntax). This can be especially useful with RSpace, as you can add links to your existing RSpace elements, such as a file in your gallery: [GL2960](https://rspace.ntnu.no/globalId/GL2960).

### Code listings

You can also add code listings. In markdown, you can add the code language to format the code according to the language you are listing. However, when this is rendered in html, the formatting is lost unless you can find a suitable extension to use when converting to html!

Python code:
```python
import hyperspy.api as hs
signal = hs.load('mydata.hspy')
signal.plot(norm='symlog')
```

Bash code:
```bash
conda create -n RSpace rspace-client=2.5.0 tabulate markdown pymdown-extensions json2html jupyter jupyterlab matplotlib numpy<2.0.0 scipy
```

# EPFL CS411 Digital Education Jupyter Notebook

This repository is for the Jupyter Notebook materials for [_CS411 Digital Education_](https://edu.epfl.ch/coursebook/en/digital-education-CS-411) at EPFL.

## Table of Contents

- [EPFL CS411 Digital Education Jupyter Notebook](#epfl-cs411-digital-education-jupyter-notebook)
  - [Table of Contents](#table-of-contents)
  - [Handbook](#handbook)
    - [How to Create a Notebook](#how-to-create-a-notebook)
    - [Integrating a Quiz](#integrating-a-quiz)
    - [Inserting an Image](#inserting-an-image)
      - [Option One](#option-one)
      - [Option Two](#option-two)
    - [Integrating a Video](#integrating-a-video)
    - [Formatting Text](#formatting-text)
  - [Resources](#resources)
    - [On our Jupyter Notebooks for Education Website](#on-our-jupyter-notebooks-for-education-website)
    - [In our Documentation](#in-our-documentation)

## Handbook

Here are some instructions for you to get started with creating your Jupyter Notebook. If you are already
very familiar with Jupyter Notebook, you can skip this section.

### How to Create a Notebook

1. Connect to [Noto](https://noto.epfl.ch).
2. Open the folder “CS411-notebookexamples”.
3. Create a new notebook:
   - Click on the blue `+` button at the top left of the workspace.
   - Select `Python 3` (or another language if you prefer) in the notebook category.
4. Rename your notebook (right-click on your notebook, then choose `Rename` in the menu).
5. Add some content:
   1. Add a new cell to your notebook (`+` button at the top of the notebook).
   2. Convert it to a Markdown cell (dropdown menu at the top of the notebook).
   3. Write some text and then `execute` the cell to render it.

### Integrating a Quiz

1. Create an “interactive content” activity in Moodle (H5P).
2. Check the visibility of the activity
   - Who has access to the course page?
   - Is the activity visible/available?
3. Find the HTML code to embed the activity (iFrame)

```
<iframe src="https://moodle.epfl.ch/mod/hvp/embed.php?id=1213682" width="1556" height="310" frameborder="0" allowfullscreen="allowfullscreen" title="MonthsQuestion">
</iframe>
```

4. Create a code cell which displays the iFrame

```
from IPython.display import IFrame

IFrame('https://moodle.epfl.ch/mod/hvp/embed.php?id=1213682', 500, 350)
```

> More details [here](https://go.epfl.ch/noto-quiz).

### Inserting an Image

#### Option One

1. Navigate to a folder into your workspace.
2. Drag-and-drop the image file onto your workspace to upload it.
3. Use Markdown or HMTL to insert the image into your notebook using the path to the image file.

```
![alternative text](path-to-image)
<img src="path-to-image" alt="Alternative text" />
```

#### Option Two

1. Edit a Markdown cell.
2. Drag-and-drop your image directly onto that cell.

### Integrating a Video

1. Find the HTML code to embed the video (iFrame).

```
<iframe src="https://tube.switch.ch/embed/QYUxxtMawn" width="640" height="360" frameborder="0" allow="fullscreen" allowfullscreen>
</iframe>
```

2. Create a code cell which displays the iFrame.

```
from IPython.display import IFrame

IFrame('https://tube.switch.ch/embed/QYUxxtMawn', 640, 360)
```

### Formatting Text

1. Create a highlighted “activity” paragraph:

```
<div style="padding:8px 0px 8px 15px;border-left:3px solid #B51F1F;
background-color:#F3F3F3;">
    <span style="font-weight:bold;text-decoration:underline;">Activity</span>
    <br/>
    <!-- Execute the code cell below so that the necessary libraries get imported. -->
</div>
```

2. Create a link to another notebook:

```
[Text of the link](path-to-notebook.ipynb)
<a href="path-to-notebook.ipynb"/>Text of the link</a>
```

## Resources

### On our Jupyter Notebooks for Education Website

- [Interactive Textbooks](https://go.epfl.ch/interactivetextbooks)
- [Exercise Worksheets](https://go.epfl.ch/exerciseworksheets)
- [Notebooks Developed by Other EPFL Teachers](https://go.epfl.ch/notebookexamples)

### In our Documentation

- [Sharing Notebooks](https:/go.epfl.ch/noto-share) with your students on Noto.
- [Embedding SpeakUp polls (or chats)](https:/go.epfl.ch/noto-polls) into Notebooks.
- [Collecting student feedback](https://go.epfl.ch/noto-feedback) into notebooks using an integrated survey.

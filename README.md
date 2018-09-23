# PDDOC
PureData documentation generator

 
This is a generator that creates *-help.pd files from single **pddoc**-formatted files and another .pd file from XML that contains objects, short descriptions and links to help files.

---

Requires: pycairo
  

  
_    | _   
--- | --- 
 **pd_doc2pd** | Converts pddoc file to PureData help patch 
 **pd_doc2html** | Converts pddoc file to HTML file 
 **pd_makelibrary** | Creates XML file for set of pddoc files 
 **pd_lib2pd** | Converts XML file to PureData patch with objects links to help files 
 **pd_cat2pd** | Converts XML file with category info to separate patch with object links 


---
## 1. XML file

```xml
<library xmlns:xi="http://www.w3.org/2001/XInclude" name="--your-library-name--" version="1.0">
  <category name="--category--">
    <entry descr="Object description" name="the_object" ref_view="object">
      <xi:include href="the_object.pddoc" parse="xml"/>
    </entry>
  </category>
 <meta>
    <version> % </version>
    <authors>
      <author> % </author>
    </authors>
  </meta>
 </library>
```
### library
- **name** (required)

### category
- **name** (required)

### entry
- **name** (required)
- **ref_view** (required):
    - object
    - link      (for UI objects)

XML file for category:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<category-info version="1.0">
description
</category-info>
```

---
## 2. pddoc file

```xml
<?xml version="1.0" encoding="utf-8"?>
<pddoc version="1.0">
    <object name="the_object">
        <title>the_object</title>
        <meta>
            <authors>
                <author> % </author>
            </authors>
            <description>% </description>
            <license> % </license>
            <library> % </library>
            <category> % </category>
            <keywords> % </keywords>
            <since> % </since>
        </meta>
        <info>
            <par> Paragraph text </par>
        </info>
        <arguments>
            <argument name="ARG_NAME" type="symbol">argument name</argument>
        </arguments>
        <properties>
            <property name="@property_name" type="symbol">property name</property>
        </properties>
        <inlets>
            <inlet>
                <xinfo on="bang">detailed description</xinfo>
            </inlet>
        </inlets>
        <outlets>
            <outlet>description</outlet>
        </outlets>
        <example>
            <pdascii>
<![CDATA[

[message_box(                                 
|
[object_box]

]]>
            </pdascii>
        </example>
    </object>
</pddoc>
```
### header:
- `<pddoc>`
    - **version** (required)
- `<object>`
    - **name** (required)
- `<title>`
- `<meta>`
    - `<authors>`
    - `<description>`
    - `<license>`
    - `<library>`
    - `<category>`
    - `<keywords>`
    - `<since>`
   
### info
```xml
<info>
    <par> Paragraph text </par>
</info>
```
### arguments
- **name** (required)
- **type** (required):
    - int
    - float
    - symbol
    - atom - int, float or symbol
    - list - list of atoms
    
### properties

```xml
<properties>
    <property name="PROP" type="TYPE">description</property>
</properties>
```

- **name** (required)
- **type** (required):
    - int
    - float
    - symbol
    - atom - int, float or symbol
    - list - list of atoms
    - alias - alias for other property
    - flag - property that is **True** when specified, otherwise **False**
- **readonly**
- **units** - value unit from list:
    - herz
    - kiloherz
    - decibell
    - millisecond
    - second
    - bpm
    - percent
- **minvalue** - minimum allowed value
- **maxvalue** - maximum allowed value
- **default** - default value, if not specified
- **enum** - comma separated list of allowed values
    ```xml 
    <property enum="A,B,C"/>
    ```
    
### inlets
```xml
<inlets dynamic="true">
    <inlet type="TYPE" number="XXX">
        <xinfo on="symbol"></xinfo>
    </inlet>
</inlets>
```

- **dynamic** *(optional)* - if True, external has dynamic number of inlets, otherwise fixed.
- **type** *(optional)* - inlet type:
    - control
    - audio
- **number** *(optional)* - manually specified inlet number: number, or "n", or "n+1", or "n-1", or "..."
- **on** *(optional)* - describe reaction on input data type. Data types:
    - atom
    - int
    - float
    - list
    - symbol
    - pointer
    - any
    - data - for additional data types
    
### outlets
```xml
<outlets>
    <outlet>
        description
    </outlet>
</outlets>
```

### example
```
<example>
    <pdascii>
<![CDATA[

[message_box(                                 
|
[object_box]

]]>
    </pdascii>
</example>
```

- [*value*( - message box
- [*value*] - object box
- [T] - toggle
- [B] - bang



    


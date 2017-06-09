# PDDOC
PureData documentation generator

## XML
for generation *-help.pd files used **pddoc** format

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

    


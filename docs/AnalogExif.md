# AnalogExif XMP Schema

AnalogExif defines a custom XMP schema to store film-related metadata in your image files.  
Most XMP parsers will ignore the schema validation step, but the full RDF definition is available online for reference:  
<https://analogexif.sourceforge.net/ns>

---

## Table of Contents

- [ExposureNumber](#exposurenumber)  
- [LensSerialNumber](#lensserialnumber)  
- [RollId](#rollid)  
- [FilmMaker](#filmmaker)  
- [Film](#film)  
- [FilmAlias](#filmalias)  
- [FilmGrain](#filmgrain)  
- [FilmType](#filmtype)  
- [Developer](#developer)  
- [DevelopProcess](#developprocess)  
- [DeveloperMaker](#developermaker)  
- [DeveloperDilution](#developerdilution)  
- [DevelopTime](#developtime)  
- [Lab](#lab)  
- [LabAddress](#labaddress)  
- [Filter](#filter)  
- [ScannerMaker](#scannermaker)  
- [Scanner](#scanner)  
- [ScannerSoftware](#scannersoftware)  

---

## Fields

### ExposureNumber  
- **XMP Path:** `Xmp.AnalogExif.ExposureNumber`  
- **Type:** Integer  
- **Description:** Exposure number of the frame. Can be auto-filled when importing several files at once.

---

### LensSerialNumber  
- **XMP Path:** `Xmp.AnalogExif.LensSerialNumber`  
- **Type:** String  
- **Description:** Serial number of the lens used.

---

### RollId  
- **XMP Path:** `Xmp.AnalogExif.RollId`  
- **Type:** String  
- **Description:** Identifier of the film roll.

---

### FilmMaker  
- **XMP Path:** `Xmp.AnalogExif.FilmMaker`  
- **Type:** String  
- **Description:** Film manufacturer (e.g., “Fuji”).

---

### Film  
- **XMP Path:** `Xmp.AnalogExif.Film`  
- **Type:** String  
- **Description:** Full film name (including manufacturer), such as “Fuji Velvia 50”.

---

### FilmAlias  
- **XMP Path:** `Xmp.AnalogExif.FilmAlias`  
- **Type:** String  
- **Description:** Common alias for the film (e.g., “RVP 50”).

---

### FilmGrain  
- **XMP Path:** `Xmp.AnalogExif.FilmGrain`  
- **Type:** Integer  
- **Description:** RMS value of film grain (e.g., “9”).

---

### FilmType  
- **XMP Path:** `Xmp.AnalogExif.FilmType`  
- **Type:** Predefined string  
- **Description:** Film format/type.  
- **Available values:**  
  - 135  
  - 120  
  - 220  
  - APS  
  - 4×5  
  - 8×10  
  - Type 600  
  - 127  
  - Disc  
  - Paper  
  - 126  
  - 101  
  - … (see full list below)  
  - SX-70  
  - Type 37  
  - Type 47  
  - Type 88  
  - Type 100

*(Complete list of all supported formats can be found in the schema RDF.)*

---

### Developer  
- **XMP Path:** `Xmp.AnalogExif.Developer`  
- **Type:** String  
- **Description:** Name of the chemical developer used (e.g., “XTOL”).

---

### DevelopProcess  
- **XMP Path:** `Xmp.AnalogExif.DevelopProcess`  
- **Type:** String  
- **Description:** Film process (e.g., “E-6”).

---

### DeveloperMaker  
- **XMP Path:** `Xmp.AnalogExif.DeveloperMaker`  
- **Type:** String  
- **Description:** Manufacturer of the developer (e.g., “Kodak”).

---

### DeveloperDilution  
- **XMP Path:** `Xmp.AnalogExif.DeveloperDilution`  
- **Type:** String  
- **Description:** Dilution ratio of the developer (e.g., “1:14”).

---

### DevelopTime  
- **XMP Path:** `Xmp.AnalogExif.DevelopTime`  
- **Type:** String  
- **Description:** Development time (e.g., “13 min”).

---

### Lab  
- **XMP Path:** `Xmp.AnalogExif.Lab`  
- **Type:** String  
- **Description:** Processing lab name.

---

### LabAddress  
- **XMP Path:** `Xmp.AnalogExif.LabAddress`  
- **Type:** String  
- **Description:** Address of the processing lab.

---

### Filter  
- **XMP Path:** `Xmp.AnalogExif.Filter`  
- **Type:** String  
- **Description:** Lens or color filter used (e.g., “Hoya R72”).

---

### ScannerMaker  
- **XMP Path:** `Xmp.AnalogExif.ScannerMaker`  
- **Type:** String  
- **Description:** Manufacturer of the scanner (e.g., “Epson”).

---

### Scanner  
- **XMP Path:** `Xmp.AnalogExif.Scanner`  
- **Type:** String  
- **Description:** Scanner model (e.g., “Epson Perfection 4490 Photo”).

---

### ScannerSoftware  
- **XMP Path:** `Xmp.AnalogExif.ScannerSoftware`  
- **Type:** String  
- **Description:** Software used for scanning (e.g., “Silverfast”).

---

<p align="center">
  <em>Generated from the AnalogExif XMP schema documentation.</em>  
</p>

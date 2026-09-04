# Zero-Copy Boundary Audit: Myth vs. Reality

**Audit Date:** September 2026  
**Auditor:** Performance Systems Engineer & Memory Auditor  
**Subject:** Zero-Copy Claims in Kuwala v0.2.0  
**Status:** TECHNICAL DEBT IDENTIFIED  

---

## 1. Executive Summary

Marketing claims in quantitative software frequently use the term "zero-copy" loosely. This hostile audit inspected every critical memory boundary in Kuwala to determine whether zero-copy is actually achieved or if memory buffers are cloned.

---

## 2. Component-by-Component Memory Boundary Audit

### A. Python to Rust Boundary (`kuwala_core/src/lib.rs`)
- **Claim:** "Zero-copy vectorized option pricing and IV inversion."
- **Reality:** **FALSE (Memory Cloned).**
  In `py_implied_volatility_batch`:
  ```rust
  #[pyfunction]
  pub fn py_implied_volatility_batch(
      py: Python<'_>,
      prices: Vec<f64>,
      spots: Vec<f64>,
      strikes: Vec<f64>,
      ttms: Vec<f64>,
      rates: Vec<f64>,
      dividends: Vec<f64>,
      is_calls: Vec<bool>,
  ) -> PyResult<PyObject>
  ```
  Passing `Vec<f64>` across PyO3 requires copying data from Python NumPy arrays into Rust heaps. Furthermore, returning `PyObject` allocates a `PyList`, iterating through the result and boxing every `f64` into a Python heap float object:
  ```rust
  let list = PyList::empty(py);
  for val in results {
      list.append(val)?;
  }
  Ok(list.into())
  ```
  **Auditor Verdict:** This is a 2x copy with Python heap boxing overhead. To achieve true zero-copy, Kuwala must accept `PyReadonlyArray1<f64>` and return `PyArray1<f64>` sharing native memory.

### B. Python to DuckDB Boundary (`kuwala/data/store.py`)
- **Claim:** "Zero-copy Apache Arrow data lake ingestion."
- **Reality:** **PARTIAL COPY.**
  In `write_chain`:
  ```python
  if isinstance(chain, pa.Table):
      df = chain.to_pandas()
      self.conn.register("temp_arrow", df)
  ```
  Calling `.to_pandas()` on an Arrow Table converts Arrow columnar memory into pandas series arrays, inducing memory duplication and type conversions.
  **Auditor Verdict:** DuckDB natively supports registering PyArrow tables directly (`self.conn.register('temp_arrow', chain)`). The `.to_pandas()` call must be eliminated.

### C. Parquet Disk to Query Engine Boundary
- **Claim:** "Zero-copy out-of-core columnar scanning."
- **Reality:** **VERIFIED TRUE.**
  DuckDB memory-maps Parquet files directly from disk, loading only projection columns into memory via vectorized vector batches without copying entire datasets into RAM.

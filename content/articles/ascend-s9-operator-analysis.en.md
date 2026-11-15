## Five operator patterns

My [July 2026 S9 analysis](https://blog.csdn.net/ruiqideng/article/details/163351391) organizes five named tasks—Concat, Greater, IndexAdd, Transpose, and SquareSumV1—by the work each kernel must perform. The [official S9 competition page](https://www.hiascend.com/developer/contests/details/41ffbad2024e4ccfa43520c57ffa7b9e) describes a five-task performance competition with accuracy validation. The original analysis is a set of design hypotheses: it does not supply an implementation, benchmark, score, or evidence that any suggested optimization was measured.

The five patterns are segmented copying, elementwise comparison with broadcasting, indexed accumulation, data-layout transformation, and map-plus-reduction. Exact supported shapes, types, reference semantics, hardware, and scoring conditions must come from the relevant task package, not from these generic examples.

## Concat: move segments efficiently

For a contiguous input, collapsing dimensions around the concatenation axis gives a useful planning model: `[outer, concat_axis, inner]`. Each input contributes a segment to the corresponding output slice. Large contiguous segments can support long transfers; an inner dimension of one can instead produce many short segments. The input count and segment sizes can make work partitioned by tensor count very uneven.

A candidate approach is to partition output byte ranges, precompute input offsets, and handle alignment and tails explicitly. Buffering or overlapping transfers may help when the device, data shape, and transfer APIs support it; extra buffering also consumes on-chip memory. A producer that writes directly into final output positions may eliminate a separate concatenation, but only if ordering, ownership, and interface semantics permit it. These are hypotheses to profile, not measured results.

## Greater: broadcasting and comparison semantics

Elementwise comparison performs little arithmetic per input and output byte. At small sizes, launch and setup can be significant; at larger sizes, data movement or address calculation may dominate. A general broadcast implementation maps output indices to input indices, using a zero stride along broadcast dimensions.

Specializing equal-shape and scalar cases can avoid repeated multidimensional division. Any specialization must preserve the reference dtype and comparison semantics, including NaN and infinities where they are in scope. If a following operation consumes the mask, fusing the two can avoid materializing it, but this requires an allowed fused interface and equivalent behavior. PyTorch documents the general [broadcasting rules](https://docs.pytorch.org/docs/stable/notes/broadcasting.html).

## IndexAdd: repeated indices change the algorithm

An indexed accumulation adds each source slice to an output slice selected by the index. Repeated indices are the central correctness constraint: concurrent non-atomic read-modify-write operations to the same element can lose updates. PyTorch's [index_add_ reference](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.index_add_.html) specifies the operation and notes possible nondeterminism on CUDA; that CUDA note is not a claim about Ascend behavior.

One option assigns each output region to a single worker and scans the relevant indices; another partitions indices and uses supported atomic updates. A third groups repeated indices before writing. These approaches trade repeated index reads, parallelism, contention, workspace, and grouping overhead. The best choice depends on the shape and index distribution. In particular, duplicate-index frequency may be unknown without inspecting input data; its measurement or estimation has a cost and cannot be assumed available to host-side tiling.

Floating-point addition order can affect results even when updates are race-free. Correctness tests need duplicate indices, empty or small cases where supported, and the task's specified numerical tolerance. Check the device and CANN version for atomic dtype and API support before selecting an implementation.

## Transpose: a view is different from a copy

A permutation can change logical strides without physically moving data: PyTorch lists `permute` among its [tensor view operations](https://docs.pytorch.org/docs/stable/tensor_view.html). A competition kernel may instead require an independently materialized output. The task's output and layout contract decides which behavior is correct.

For a materialized transpose, reading rows contiguously can make destination writes strided, and the reverse can make reads strided. A tiled implementation can stage a block in on-chip memory, rearrange it, and write it back in larger contiguous segments. Tile sizes, alignment, tails, on-chip capacity, and available device instructions constrain the design. Layout propagation or fusion can remove a copy only if all producers and consumers accept the resulting layout.

## SquareSumV1: reduce without a full intermediate

The analyzed operation squares elements and reduces them over specified axes; `keepdim` controls whether reduced dimensions remain in the result. The [PyTorch sum reference](https://docs.pytorch.org/docs/stable/generated/torch.sum.html) documents axis, output shape, and dtype options. Actual competition dtype and error requirements must be checked separately.

The design opportunity is to combine square and reduction while values are on chip instead of writing a full squared tensor to global memory. A contiguous inner reduction and a strided middle-axis reduction have different access patterns. For a small number of outputs and long reductions, multiple workers may need partial sums and a second stage; that requires workspace and synchronization. Accumulating in higher precision is a possible accuracy strategy only if the task's dtype and tolerance contract permits it.

## A useful evaluation plan

Start with a correct baseline per operator. Record the exact SoC, CANN and driver versions, input shapes and types, reference implementation, tolerances, and timing boundaries. Cover alignment tails, broadcast patterns, repeated indices, reduction axes, special floating-point values where relevant, and sizes ranging from launch-bound to bandwidth-bound. Compare candidate paths on the same inputs and include any workspace or extra kernel cost. The original post proposes optimization ideas but reports no measured speedup or contest result; the ranking of approaches remains an experiment.

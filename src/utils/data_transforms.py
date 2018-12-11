import numpy

'''
This is a torch-free file that exists to massage data
From sparse to dense or dense to sparse, etc.

This can also convert from sparse to sparse to rearrange formats
For example, larcv BatchFillerSparseTensor2D (and 3D) output data
with the format of 
    [B, N_planes, Max_voxels, N_features] 

where N_features is 2 or 3 depending on whether or not values are included 
(or 3 or 4 in the 3D case)

# The input of a pointnet type format can work with this, but SparseConvNet
# requires a tuple of (coords, features, [batch_size, optional])


''' 

def larcvsparse_to_scnsparse_3d(input_array):
    # This format converts the larcv sparse format to
    # the tuple format required for sparseconvnet

    # First, we can split off the features (which is the pixel value)
    # and the indexes (which is everythin else)

    n_dims = input_array.shape[-1]

    split_tensors = numpy.split(input_array, n_dims, axis=-1)


    # To map out the non_zero locations now is easy:
    non_zero_inds = numpy.where(split_tensors[-1] != 0.0)

    # The batch dimension is just the first piece of the non-zero indexes:
    batch_size  = input_array.shape[0]
    batch_index = non_zero_inds[0]

    # Getting the voxel values (features) is also straightforward:
    features = numpy.expand_dims(split_tensors[-1][non_zero_inds],axis=-1)

    # Lastly, we need to stack up the coordinates, which we do here:
    dimension_list = []
    for i in range(len(split_tensors) - 1):
        dimension_list.append(split_tensors[i][non_zero_inds])

    # Tack on the batch index to this list for stacking:
    dimension_list.append(batch_index)

    # And stack this into one numpy array:
    dimension = numpy.stack(dimension_list, axis=-1)

    output_array = (dimension, features, batch_size,)
    return output_array


def larcvsparse_to_scnsparse_2d(input_array):
    # This format converts the larcv sparse format to
    # the tuple format required for sparseconvnet

    # First, we can split off the features (which is the pixel value)
    # and the indexes (which is everythin else)

    # To handle the multiplane networks, we have to split this into
    # n_planes and pass it out as a list

    n_planes = input_array.shape[1]
    batch_size = input_array.shape[0]

    raw_planes = numpy.split(input_array,n_planes, axis=1)

    output_list = []

    for i, plane in enumerate(raw_planes):
        # First, squeeze off the plane dimension from this image:
        plane = numpy.squeeze(plane, axis=1)

        # Next, figure out the x, y, value coordinates:
        x,y,val = numpy.split(plane, 3, axis=-1)

        non_zero_locs = numpy.where(val != 0.0)

        # Pull together the different dimensions:
        x = x[non_zero_locs]
        y = y[non_zero_locs]
        val = val[non_zero_locs]

        batch = non_zero_locs[0]

        # dimension = numpy.concatenate([x,y,batch], axis=0)
        # dimension = numpy.stack([x,y,batch], axis=-1)
        dimension = numpy.stack([x,y], axis=-1)


        output_list.append(
            (dimension, val)
            )


    return output_list

def larcvsparse_to_dense(input_array):
    raise Exception("This function not yet implemented")

def larcvdense_to_scnsparse_3d(input_array):
    # Convert a full scale 3D tensor (actually 5D, batch + channel at the end)


    n_dims = 4

    # To map out the non_zero locations now is easy:
    batch, x, y, z, val = numpy.where(input_array != 0.0)

    features = input_array[batch,x,y,z,val]

    # The batch dimension is just the first piece of the non-zero indexes:
    batch_size  = input_array.shape[0]

    # And stack this into one numpy array:
    dimension = numpy.stack([x,y,z,batch], axis=-1)

    output_array = (dimension, features, batch_size)

    return output_array

